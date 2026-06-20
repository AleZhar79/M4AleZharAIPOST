"""
БЛОК 4 — клиент OpenAI / OpenRouter.

OpenRouter — это прокси над разными LLM (GPT, Claude, DeepSeek, Llama).
Он совместим с API OpenAI, поэтому мы используем библиотеку `openai`,
просто указываем другой base_url.

Что важно понять:
1. Клиент создаётся ОДИН раз на модуль (а не на каждый вызов) —
   так быстрее и не плодим лишних HTTP-соединений.
2. Любой сетевой вызов может упасть. Мы ловим типовые ошибки
   и поднимаем своё исключение AIGenerationError — чтобы вышестоящий
   код (Celery-таск, эндпоинт) знал: "это ошибка AI, не баг кода".
3. Все секреты — из settings, никаких хардкодов.
"""
from openai import (
    OpenAI,
    APIError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
)

from app.config import settings
from app.utils import get_logger

log = get_logger(__name__)


class AIGenerationError(Exception):
    """Любая ошибка генерации, которую мы хотим показать пользователю."""


# Создаём клиент один раз. Если ключа нет — клиент всё равно создастся,
# но любой вызов упадёт с AuthenticationError. Это нормально для учебного проекта.
_client = OpenAI(
    api_key=settings.openai_api_key or "missing-key",
    base_url=settings.openai_base_url,
    timeout=60.0,  # AI может думать долго, но не вечно
)


def call_openai(prompt: str) -> str:
    """
    Делает реальный вызов LLM через OpenRouter.
    Возвращает текст ответа модели.
    Кидает AIGenerationError при любой проблеме.
    """
    if not settings.openai_api_key:
        raise AIGenerationError(
            "OPENAI_API_KEY не задан в .env — поставь ключ от OpenRouter "
            "(начинается с sk-or-v1-...) и перезапусти worker."
        )

    log.info(
        f"[openai] вызов модели={settings.openai_model}, "
        f"prompt (первые 100 символов): {prompt[:100]!r}"
    )

    try:
        response = _client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
    except AuthenticationError as e:
        log.error(f"[openai] неверный API-ключ: {e}")
        raise AIGenerationError("Неверный API-ключ OpenRouter. Проверь .env.") from e
    except RateLimitError as e:
        log.warning(f"[openai] превышен лимит запросов: {e}")
        raise AIGenerationError(
            "Превышен лимит запросов OpenRouter (на free-tier ~20/мин, ~50/день). "
            "Подожди немного или возьми платную модель."
        ) from e
    except APITimeoutError as e:
        log.warning(f"[openai] таймаут запроса: {e}")
        raise AIGenerationError("OpenRouter не ответил вовремя (таймаут).") from e
    except APIError as e:
        log.error(f"[openai] ошибка API: {e}")
        raise AIGenerationError(f"Ошибка OpenRouter API: {e}") from e

    # Защита от пустого ответа
    if not response.choices or not response.choices[0].message.content:
        raise AIGenerationError("Модель вернула пустой ответ.")

    text = response.choices[0].message.content.strip()
    log.info(f"[openai] получен ответ длиной {len(text)} символов")
    return text

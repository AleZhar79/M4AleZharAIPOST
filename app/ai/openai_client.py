"""
БЛОК 4 — клиент OpenAI (СКЕЛЕТ / MOCK).

Пока не делаем реальный вызов API.
Возвращаем фиксированный текст, чтобы проект работал без ключа.

КОГДА БУДЕМ ДЕЛАТЬ БЛОК 4 ВСЕРЬЁЗ:
1. Добавим в requirements.txt: openai==1.51.0
2. Заменим тело call_openai() на реальный вызов:

    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

3. Добавим обработку ошибок: RateLimitError, APIError, APITimeoutError.
"""
from app.config import settings
from app.utils import get_logger

log = get_logger(__name__)


def call_openai(prompt: str) -> str:
    """
    Mock-реализация. Возвращает фиксированный «сгенерированный» текст.
    Будет заменена на реальный вызов OpenAI в Блоке 4.
    """
    if not settings.openai_api_key:
        log.info("[MOCK OpenAI] OPENAI_API_KEY не задан — работаем в режиме заглушки")
    else:
        log.info("[MOCK OpenAI] ключ задан, но реальный вызов будет в Блоке 4")

    log.info(f"[MOCK OpenAI] prompt (первые 100 символов): {prompt[:100]!r}")

    return (
        "🚀 [MOCK ПОСТ] Это заглушка ответа OpenAI.\n\n"
        "Когда мы подключим реальный API в Блоке 4, тут будет настоящий "
        "сгенерированный пост на основе новости.\n\n"
        "👉 Подписывайся, чтобы не пропустить!"
    )

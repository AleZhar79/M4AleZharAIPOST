"""
БЛОК 5 — клиент Telethon. РЕАЛЬНАЯ ВЕРСИЯ.

Telethon работает от имени пользователя (user-account), а не бота.
Это значит:
  - При первом запуске Telegram пришлёт SMS-код на TELEGRAM_PHONE.
  - После ввода кода создастся файл tg_session.session — это твоя сессия.
  - Все последующие запуски используют этот файл, SMS больше не нужны.

ВАЖНО: файл tg_session.session = доступ к твоему Telegram-аккаунту.
Никогда не коммить его в git, не пересылай никому, не выкладывай скриншоты.

Перед первым запуском воркера/uvicorn:
    python scripts/tg_login.py
— это интерактивно создаст сессию и проверит, что канал доступен.

Публичный контракт модуля:
    send_message(channel, text) -> int (id отправленного сообщения)
    fetch_messages(channel, limit) -> list[dict]
    + send_message_mock / fetch_messages_mock — алиасы для обратной совместимости.
"""
import asyncio
from typing import Any, Dict, List

from telethon.sync import TelegramClient
from telethon.errors import (
    ChannelPrivateError,
    ChatWriteForbiddenError,
    FloodWaitError,
    SessionPasswordNeededError,
)

from app.config import settings
from app.utils import get_logger

log = get_logger(__name__)


class TelegramPublishError(Exception):
    """Бизнес-исключение для понятных ошибок публикации."""


def _check_credentials() -> None:
    """Жёстко проверяем, что .env заполнен. Лучше упасть сразу с понятным текстом,
    чем получить невнятную ошибку из глубины Telethon."""
    if not settings.telegram_api_id or not settings.telegram_api_hash:
        raise TelegramPublishError(
            "Не заполнены TELEGRAM_API_ID или TELEGRAM_API_HASH в .env"
        )
    if not settings.telegram_phone:
        raise TelegramPublishError("Не заполнен TELEGRAM_PHONE в .env")
    if not settings.telegram_channel:
        raise TelegramPublishError("Не заполнен TELEGRAM_CHANNEL в .env")


def _ensure_event_loop() -> None:
    """
    Telethon внутри живёт на asyncio. Под капотом он ищет event loop в текущем потоке.
    В обычной консоли / Celery worker с --pool=solo loop есть.
    А вот в FastAPI синхронные эндпоинты работают в отдельных anyio worker threads,
    и там loop приходится создавать руками — иначе падает
    `RuntimeError: There is no current event loop in thread 'AnyIO worker thread'`.
    """
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        # Нет loop'а в этом потоке — создаём и привязываем.
        asyncio.set_event_loop(asyncio.new_event_loop())


def _make_client() -> TelegramClient:
    """Создаёт TelegramClient. Сессия читается из файла settings.telegram_session_name."""
    _ensure_event_loop()
    return TelegramClient(
        settings.telegram_session_name,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )


# ==================== ОТПРАВКА ====================

def send_message(channel: str, text: str) -> int:
    """
    Отправляет текст в канал. Возвращает id сообщения в Telegram.

    Это синхронная функция — внутри Celery (--pool=solo на Windows) так проще.
    """
    _check_credentials()

    client = _make_client()
    try:
        # client.start():
        #   - если сессия валидна → просто подключится;
        #   - если сессии нет → попробует попросить SMS-код через input(),
        #     а в Celery/uvicorn input() не сработает — поэтому первый запуск
        #     ОБЯЗАТЕЛЬНО через scripts/tg_login.py.
        client.start(phone=settings.telegram_phone)

        message = client.send_message(
            entity=channel,
            message=text,
            parse_mode="md",     # поддержка markdown
            link_preview=True,
        )
        log.info(f"[telethon] отправлено в {channel}, message_id={message.id}")
        return message.id

    except FloodWaitError as e:
        raise TelegramPublishError(
            f"Telegram попросил подождать {e.seconds} сек (flood wait)"
        ) from e
    except ChannelPrivateError as e:
        raise TelegramPublishError(
            "Канал приватный или нет доступа. Проверь @username и что ты админ."
        ) from e
    except ChatWriteForbiddenError as e:
        raise TelegramPublishError(
            "Нет прав писать в канал. Сделай аккаунт админом канала."
        ) from e
    except SessionPasswordNeededError as e:
        raise TelegramPublishError(
            "На аккаунте включена двухфакторная авторизация (cloud password). "
            "Запусти scripts/tg_login.py — он сможет её спросить интерактивно."
        ) from e
    except Exception as e:
        raise TelegramPublishError(
            f"Ошибка публикации: {type(e).__name__}: {e}"
        ) from e
    finally:
        client.disconnect()


# ==================== ЧТЕНИЕ ====================

def fetch_messages(channel: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Читает последние сообщения из канала. Используется парсером Telegram-источников."""
    _check_credentials()

    client = _make_client()
    try:
        client.start(phone=settings.telegram_phone)

        result: List[Dict[str, Any]] = []
        for msg in client.iter_messages(channel, limit=limit):
            if not msg.message:
                continue  # пропускаем посты без текста (стикеры, опросы и т.п.)
            result.append({
                "title": msg.message[:200],
                "url": f"https://t.me/{channel.lstrip('@')}/{msg.id}",
                "summary": msg.message[:500],
                "source": channel,
                "published_at": msg.date,
                "raw_text": msg.message,
            })
        return result
    finally:
        client.disconnect()


# ==================== АЛИАСЫ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ ====================
# Раньше publisher.py и telegram-парсер дёргали *_mock-функции.
# Сохраняем имена, чтобы старый код не падал. Внутри — реальные вызовы.

def send_message_mock(channel: str, text: str) -> bool:
    """Алиас для совместимости. Теперь шлёт реально."""
    try:
        send_message(channel, text)
        return True
    except TelegramPublishError as e:
        log.error(f"[telethon] не отправлено в {channel}: {e}")
        return False


def fetch_messages_mock(channel: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Алиас для совместимости. Теперь читает реально."""
    return fetch_messages(channel, limit)

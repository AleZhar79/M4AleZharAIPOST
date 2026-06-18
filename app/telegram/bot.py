"""
БЛОК 5 — клиент Telethon (СКЕЛЕТ / MOCK).

Тут будет общий TelegramClient: он же читает каналы (заменит mock из
app/news_parser/telegram.py) и он же публикует посты.

Сейчас функции — заглушки.

КОГДА БУДЕМ ДЕЛАТЬ БЛОК 5 ВСЕРЬЁЗ:
1. Добавим в requirements.txt: telethon==1.36.0
2. Получим API_ID и API_HASH на https://my.telegram.org
3. Заменим тела функций ниже на реальные вызовы:

    from telethon.sync import TelegramClient
    client = TelegramClient("aibot_session", settings.telegram_api_id, settings.telegram_api_hash)

    def send_message(channel: str, text: str):
        with client:
            client.send_message(channel, text)

    def fetch_messages(channel: str, limit: int = 5):
        with client:
            return list(client.iter_messages(channel, limit=limit))
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.config import settings
from app.utils import get_logger

log = get_logger(__name__)


def send_message_mock(channel: str, text: str) -> bool:
    """
    Mock-публикация: просто пишет в лог, что бы отправилось.
    Возвращает True, имитируя успех.
    """
    if not (settings.telegram_api_id and settings.telegram_api_hash):
        log.info("[MOCK Telegram] API_ID/API_HASH не заданы — работаем в режиме заглушки")
    log.info(f"[MOCK Telegram] -> channel={channel}\n--- TEXT ---\n{text}\n------------")
    return True


def fetch_messages_mock(channel: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Mock-чтение канала. То же, что в app/news_parser/telegram.py:
    возвращает фейковые сообщения. В Блоке 5 этот код станет единственным
    источником правды для Telegram, а парсер в news_parser/telegram.py
    будет дёргать его.
    """
    now = datetime.utcnow()
    return [
        {
            "title": f"[MOCK BOT] Сообщение #{i + 1} из {channel}",
            "url": f"https://t.me/{channel.lstrip('@')}/{2000 + i}",
            "summary": f"Mock-текст из {channel}",
            "source": channel,
            "published_at": now - timedelta(minutes=i * 5),
            "raw_text": f"Полный mock-текст #{i + 1} из {channel}.",
        }
        for i in range(limit)
    ]

"""
Парсер Telegram-каналов.

На этом этапе — ЗАГЛУШКА (mock).
Возвращаем фейковые сообщения, чтобы не зависеть от Telethon, API_ID/API_HASH и сессии.
Реальный парсер подключим в Блоке 5 одновременно с публикацией.

В реальной версии тут будет TelegramClient из Telethon и iter_messages().
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any


def parse_telegram_channel(channel: str, source_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    ВРЕМЕННАЯ заглушка. Возвращает фейковые сообщения для канала.
    В Блоке 5 заменим на реальный вызов Telethon.
    """
    now = datetime.utcnow()
    fake_messages = []

    for i in range(limit):
        fake_messages.append({
            "title": f"[MOCK] Сообщение #{i + 1} из канала {channel}",
            "url": f"https://t.me/{channel.lstrip('@')}/{1000 + i}",
            "summary": f"Это тестовое сообщение из канала {channel}. Текст будет заменён, когда подключим Telethon.",
            "source": source_name,
            "published_at": now - timedelta(minutes=i * 10),
            "raw_text": f"Полный текст mock-сообщения #{i + 1} из {channel}.",
        })

    return fake_messages

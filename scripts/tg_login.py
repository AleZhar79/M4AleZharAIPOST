"""
Разовый скрипт первой авторизации Telethon.

Запускать ОДИН РАЗ в обычной PowerShell с активированной venv:
    python scripts/tg_login.py

Telethon спросит код из SMS (приходит на TELEGRAM_PHONE),
после ввода создаст tg_session.session — это и есть сессия.
"""

from telethon.sync import TelegramClient
from app.config import settings


def main():
    print(f"API_ID: {settings.telegram_api_id}")
    print(f"Phone:  {settings.telegram_phone}")
    print(f"Channel: {settings.telegram_channel}")
    print()

    if not settings.telegram_api_id or not settings.telegram_api_hash:
        print("ОШИБКА: TELEGRAM_API_ID / TELEGRAM_API_HASH не заполнены в .env")
        return

    client = TelegramClient(
        settings.telegram_session_name,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )
    client.start(phone=settings.telegram_phone)

    me = client.get_me()
    print(f"\nОК. Авторизован как: {me.first_name} (id={me.id}, username=@{me.username})")

    try:
        entity = client.get_entity(settings.telegram_channel)
        print(f"Канал найден: {entity.title} (id={entity.id})")
    except Exception as e:
        print(f"ВНИМАНИЕ: канал {settings.telegram_channel} не найден или недоступен: {e}")

    client.disconnect()
    print("\nГотово. Файл tg_session.session создан.")


if __name__ == "__main__":
    main()
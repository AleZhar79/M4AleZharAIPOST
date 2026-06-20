"""
Разовый скрипт первой авторизации Telethon.

Запускать ОДИН РАЗ в обычной PowerShell с активированной venv ИЗ КОРНЯ ПРОЕКТА:
    python scripts/tg_login.py

Telethon спросит код из Telegram (приходит в чат "Telegram", не SMS),
после ввода создаст tg_session.session — это и есть сессия.

Если на аккаунте включена двухфакторная авторизация (cloud password),
Telethon дополнительно спросит пароль — это нормально.
"""
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы работал `from app.config import ...`
# даже когда скрипт запускается из подпапки scripts/.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from telethon.sync import TelegramClient
from app.config import settings


def main():
    print(f"API_ID:  {settings.telegram_api_id}")
    print(f"Phone:   {settings.telegram_phone}")
    print(f"Channel: {settings.telegram_channel}")
    print(f"Session: {settings.telegram_session_name}.session")
    print()

    if not settings.telegram_api_id or not settings.telegram_api_hash:
        print("ОШИБКА: TELEGRAM_API_ID / TELEGRAM_API_HASH не заполнены в .env")
        return
    if not settings.telegram_phone:
        print("ОШИБКА: TELEGRAM_PHONE не заполнен в .env (формат +79XXXXXXXXX)")
        return

    client = TelegramClient(
        settings.telegram_session_name,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )
    client.start(phone=settings.telegram_phone)

    me = client.get_me()
    print(f"\nОК. Авторизован как: {me.first_name} (id={me.id}, username=@{me.username})")

    if settings.telegram_channel:
        try:
            entity = client.get_entity(settings.telegram_channel)
            print(f"Канал найден: {entity.title} (id={entity.id})")
        except Exception as e:
            print(f"ВНИМАНИЕ: канал {settings.telegram_channel} не найден или недоступен: {e}")
    else:
        print("ВНИМАНИЕ: TELEGRAM_CHANNEL не задан — канал не проверяю.")

    client.disconnect()
    print(f"\nГотово. Файл {settings.telegram_session_name}.session создан в корне проекта.")


if __name__ == "__main__":
    main()

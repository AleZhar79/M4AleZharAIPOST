from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # База данных
    database_url: str = "sqlite:///./aibot.db"

    # Очередь задач
    redis_url: str = "redis://localhost:6379/0"

    # AI (OpenRouter / OpenAI-совместимый API)
    openai_api_key: str = ""
    openai_base_url: str = "https://openrouter.ai/api/v1"
    openai_model: str = "google/gemma-4-31b-it:free"

    # Telegram (Telethon — публикация от имени user-account)
    telegram_api_id: int = 0
    telegram_api_hash: str = ""
    telegram_phone: str = ""           # +7XXXXXXXXXX
    telegram_channel: str = ""         # @username канала
    telegram_session_name: str = "tg_session"
    # Оставляем для обратной совместимости — пока не используется
    telegram_bot_token: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

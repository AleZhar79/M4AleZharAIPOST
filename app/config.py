from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # База данных
    database_url: str = "sqlite:///./aibot.db"

    # Заглушки под будущие блоки (пока не используются)
    openai_api_key: str = ""
    telegram_api_id: str = ""
    telegram_api_hash: str = ""
    telegram_bot_token: str = ""
    telegram_channel: str = ""
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

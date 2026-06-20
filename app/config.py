from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # База данных
    database_url: str = "sqlite:///./aibot.db"

    # Очередь задач
    redis_url: str = "redis://localhost:6379/0"

    # AI (OpenRouter / OpenAI-совместимый API)
    openai_api_key: str = ""
    openai_base_url: str = "https://openrouter.ai/api/v1"
    openai_model: str = "deepseek/deepseek-chat-v3.1:free"

    # Заглушки под Блок 5 (Telegram)
    telegram_api_id: str = ""
    telegram_api_hash: str = ""
    telegram_bot_token: str = ""
    telegram_channel: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

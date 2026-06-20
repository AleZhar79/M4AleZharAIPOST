"""
БЛОК 5 — публикация постов в Telegram-канал.

publish_post(post) умеет:
- проверить, что пост ещё не публиковался (status != "published"),
- отправить его в канал из settings.telegram_channel,
- обновить status и published_at в базе.

Реальную работу делает app/telegram/bot.py (Telethon).
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Post
from app.telegram.bot import send_message, TelegramPublishError
from app.utils import get_logger

log = get_logger(__name__)


def publish_post(db: Session, post: Post) -> bool:
    """
    Публикует один пост в Telegram-канал.
    Возвращает True при успехе, False при ошибке.
    Любые ошибки логируем и сохраняем в БД статус 'failed' — не подымаем выше,
    чтобы HTTP-эндпоинт не падал 500-кой.
    """
    if post.status == "published":
        log.info(f"[publisher] post_id={post.id} уже опубликован, пропускаю")
        return False

    channel = settings.telegram_channel
    if not channel:
        log.error("[publisher] TELEGRAM_CHANNEL не задан в .env")
        post.status = "failed"
        db.commit()
        return False

    try:
        message_id = send_message(channel, post.generated_text)
        post.status = "published"
        post.published_at = datetime.utcnow()
        db.commit()
        log.info(
            f"[publisher] post_id={post.id} опубликован в {channel}, "
            f"tg_message_id={message_id}"
        )
        return True
    except TelegramPublishError as e:
        log.error(f"[publisher] ошибка публикации post_id={post.id}: {e}")
        post.status = "failed"
        db.commit()
        return False
    except Exception as e:
        log.error(f"[publisher] неожиданная ошибка post_id={post.id}: {type(e).__name__}: {e}")
        post.status = "failed"
        db.commit()
        return False

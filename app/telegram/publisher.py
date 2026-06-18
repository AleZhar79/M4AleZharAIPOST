"""
БЛОК 5 — публикация постов в Telegram-канал (СКЕЛЕТ).

publish_post(post) умеет:
- проверить, что пост ещё не публиковался (status != "published"),
- отправить его в канал из настроек,
- обновить status и published_at в базе.

Сейчас отправка идёт через mock из app/telegram/bot.py — в консоль.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Post
from app.telegram.bot import send_message_mock
from app.utils import get_logger

log = get_logger(__name__)


def publish_post(db: Session, post: Post) -> bool:
    """
    Публикует один пост в Telegram-канал из settings.telegram_channel.
    Возвращает True при успехе, False при ошибке.
    """
    if post.status == "published":
        log.info(f"[publisher] post_id={post.id} уже опубликован, пропускаю")
        return False

    channel = settings.telegram_channel or "@mock_channel"

    try:
        ok = send_message_mock(channel, post.generated_text)
        if ok:
            post.status = "published"
            post.published_at = datetime.utcnow()
            db.commit()
            log.info(f"[publisher] post_id={post.id} опубликован в {channel}")
            return True
        else:
            post.status = "failed"
            db.commit()
            return False
    except Exception as e:
        log.error(f"[publisher] ошибка публикации post_id={post.id}: {e}")
        post.status = "failed"
        db.commit()
        return False

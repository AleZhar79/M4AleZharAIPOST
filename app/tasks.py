"""
Celery-таски проекта.

Главная мысль: Celery — это просто способ запустить обычную функцию в фоне.
Бизнес-логика живёт в app/news_parser/ и app/ai/, а тут только обёртки.
"""
from celery_worker import celery_app
from app.database import SessionLocal
from app.models import NewsItem, Post
from app.news_parser.service import run_parsing
from app.ai.generator import generate_post_text
from app.ai.openai_client import AIGenerationError
from app.utils import get_logger

log = get_logger(__name__)


@celery_app.task(name="app.tasks.parse_all_sources_task")
def parse_all_sources_task() -> dict:
    """
    Парсинг всех включённых источников.
    Запускается вручную через /api/parse/run-async и автоматически Beat'ом каждые 30 мин.
    """
    log.info("[celery] parse_all_sources_task: старт")
    db = SessionLocal()
    try:
        stats = run_parsing(db)
        log.info(f"[celery] parse_all_sources_task: готово, stats={stats}")
        return stats
    finally:
        db.close()


@celery_app.task(name="app.tasks.generate_post_task")
def generate_post_task(news_id: int) -> dict:
    """
    Генерация поста по новости через AI.
    Создаёт запись Post со status='generated' (или 'failed' при ошибке).
    """
    log.info(f"[celery] generate_post_task(news_id={news_id}): старт")
    db = SessionLocal()
    try:
        news = db.query(NewsItem).get(news_id)
        if not news:
            log.warning(f"[celery] generate_post_task: news_id={news_id} не найдена")
            return {"status": "not_found", "news_id": news_id}

        try:
            text = generate_post_text(news)
        except AIGenerationError as e:
            # Сохраняем неудачную попытку, чтобы было видно в /api/posts/
            post = Post(news_id=news.id, generated_text=f"[FAILED] {e}", status="failed")
            db.add(post)
            db.commit()
            db.refresh(post)
            log.error(f"[celery] generate_post_task: ошибка AI — {e}")
            return {"status": "failed", "post_id": post.id, "error": str(e)}

        post = Post(news_id=news.id, generated_text=text, status="generated")
        db.add(post)
        db.commit()
        db.refresh(post)
        log.info(f"[celery] generate_post_task: пост {post.id} создан")
        return {"status": "generated", "post_id": post.id, "length": len(text)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.publish_post_task")
def publish_post_task(post_id: int) -> dict:
    """Заглушка под Блок 5."""
    log.info(f"[celery] publish_post_task(post_id={post_id}) — заглушка для Блока 5")
    return {"status": "stub", "post_id": post_id}


@celery_app.task(name="app.tasks.pipeline_task")
def pipeline_task() -> dict:
    """
    Полная цепочка: парсинг → генерация → публикация.
    Пока вызывает только парсинг. Достроим в Блоке 5.
    """
    log.info("[celery] pipeline_task: запускаю парсинг")
    parse_all_sources_task.apply_async()
    return {"status": "scheduled", "next": "parse_all_sources_task"}

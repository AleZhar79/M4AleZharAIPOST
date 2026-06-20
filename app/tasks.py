"""
Celery-таски проекта.

Главная задача — parse_all_sources_task. Она дёргает уже готовый run_parsing()
из Блока 2. Это ключевая мысль: Celery — это просто способ запустить вашу
обычную функцию в фоне. Сама бизнес-логика остаётся в одном месте.

Внутри таска мы создаём новую сессию БД через SessionLocal — потому что
get_db() из FastAPI здесь не работает (это not зависимость FastAPI).
"""
from celery_worker import celery_app
from app.database import SessionLocal
from app.news_parser.service import run_parsing
from app.utils import get_logger

log = get_logger(__name__)


@celery_app.task(name="app.tasks.parse_all_sources_task")
def parse_all_sources_task() -> dict:
    """
    Парсинг всех включённых источников.
    Запускается:
      - вручную через POST /api/parse/run-async
      - автоматически Celery Beat'ом каждые 30 минут
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
    Заглушка-задача под Блок 4. Пока ничего не делает.
    В Блоке 4 заменим тело на реальный вызов AI-генератора.
    """
    log.info(f"[celery] generate_post_task(news_id={news_id}) — заглушка для Блока 4")
    return {"status": "stub", "news_id": news_id}


@celery_app.task(name="app.tasks.publish_post_task")
def publish_post_task(post_id: int) -> dict:
    """
    Заглушка-задача под Блок 5. Пока ничего не делает.
    """
    log.info(f"[celery] publish_post_task(post_id={post_id}) — заглушка для Блока 5")
    return {"status": "stub", "post_id": post_id}


@celery_app.task(name="app.tasks.pipeline_task")
def pipeline_task() -> dict:
    """
    Полная цепочка: парсинг → генерация → публикация.
    Пока вызывает только парсинг. Достроим в Блоках 4–5.
    """
    log.info("[celery] pipeline_task: запускаю парсинг")
    parse_all_sources_task.apply_async()
    return {"status": "scheduled", "next": "parse_all_sources_task"}

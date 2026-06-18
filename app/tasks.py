"""
БЛОК 3 — Celery-таски (СКЕЛЕТ / MOCK).

Здесь будут фоновые задачи: парсинг, генерация постов, публикация.
Пока — заглушки. Они НЕ требуют запущенного Redis и НЕ импортируют Celery.
Это сделано специально, чтобы проект запускался без инфраструктуры.

Когда дойдём до Блока 3 «по-настоящему»:
1. Раскомментируем celery_app в celery_worker.py.
2. Импортируем celery_app сюда.
3. Заменим обычные функции на @celery_app.task.
4. Добавим celery beat schedule для парсинга каждые 30 минут.
"""
from app.utils import get_logger

log = get_logger(__name__)


# --- Mock-таски (обычные функции, без Celery) ---

def parse_all_sources_task() -> dict:
    """
    Будущий Celery-таск: парсинг всех включённых источников по расписанию.
    Сейчас просто пишет в лог.
    """
    log.info("[MOCK TASK] parse_all_sources_task: парсинг будет здесь, после подключения Celery")
    return {"status": "mock", "task": "parse_all_sources"}


def generate_post_task(news_id: int) -> dict:
    """
    Будущий Celery-таск: сгенерировать пост для конкретной новости через AI.
    """
    log.info(f"[MOCK TASK] generate_post_task(news_id={news_id})")
    return {"status": "mock", "task": "generate_post", "news_id": news_id}


def publish_post_task(post_id: int) -> dict:
    """
    Будущий Celery-таск: опубликовать готовый пост в Telegram.
    """
    log.info(f"[MOCK TASK] publish_post_task(post_id={post_id})")
    return {"status": "mock", "task": "publish_post", "post_id": post_id}


def pipeline_task() -> dict:
    """
    Будущая цепочка: парсинг → фильтрация → генерация → публикация.
    """
    log.info("[MOCK TASK] pipeline_task: тут будет полная цепочка фоновой обработки")
    return {"status": "mock", "task": "pipeline"}

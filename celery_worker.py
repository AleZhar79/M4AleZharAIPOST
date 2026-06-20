"""
Точка входа Celery-воркера.

Здесь создаётся экземпляр Celery-приложения с настроенным брокером (Redis)
и расписанием Celery Beat.

Запуск на Windows:
    celery -A celery_worker.celery_app worker --loglevel=info --pool=solo
    celery -A celery_worker.celery_app beat   --loglevel=info

(в двух отдельных терминалах, оба с активированным venv)
"""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "aibot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)

# Расписание Celery Beat: парсим все источники каждые 30 минут.
celery_app.conf.beat_schedule = {
    "parse-every-30-minutes": {
        "task": "app.tasks.parse_all_sources_task",
        "schedule": crontab(minute="*/30"),
    },
}
celery_app.conf.timezone = "UTC"

# Защита от слишком долгих тасков (если RSS-сайт «висит»)
celery_app.conf.task_soft_time_limit = 60   # секунд
celery_app.conf.task_time_limit = 90


if __name__ == "__main__":
    print(
        "Celery-приложение создано. Запускай воркер командой:\n"
        "  celery -A celery_worker.celery_app worker --loglevel=info --pool=solo"
    )

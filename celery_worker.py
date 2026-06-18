"""
БЛОК 3 — точка входа Celery-воркера (СКЕЛЕТ).

Сейчас Celery НЕ подключён — файл-плейсхолдер.
Запускать его пока не нужно, потому что Redis не требуется и таски в app/tasks.py
работают как обычные функции.

КОГДА БУДЕМ ДЕЛАТЬ БЛОК 3 ВСЕРЬЁЗ:
1. Добавим в requirements.txt: celery==5.4.0  redis==5.0.8
2. Раскомментируем код ниже.
3. Запустим воркер:
       celery -A celery_worker.celery_app worker --loglevel=info --pool=solo
   (флаг --pool=solo нужен на Windows)
4. Запустим Celery Beat (планировщик) отдельно:
       celery -A celery_worker.celery_app beat --loglevel=info
"""

# ============================================================
# Раскомментировать в Блоке 3
# ============================================================
# from celery import Celery
# from celery.schedules import crontab
#
# from app.config import settings
#
# celery_app = Celery(
#     "aibot",
#     broker=settings.redis_url,
#     backend=settings.redis_url,
#     include=["app.tasks"],
# )
#
# celery_app.conf.beat_schedule = {
#     "parse-every-30-minutes": {
#         "task": "app.tasks.parse_all_sources_task",
#         "schedule": crontab(minute="*/30"),
#     },
# }
# celery_app.conf.timezone = "UTC"

if __name__ == "__main__":
    print(
        "[celery_worker] Заглушка. Celery ещё не подключён — это будет в Блоке 3.\n"
        "Пока запускай только FastAPI: uvicorn app.main:app --reload"
    )

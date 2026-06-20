"""
Разовый скрипт: добавить в БД готовый набор рабочих RSS-источников.

Запуск ИЗ КОРНЯ ПРОЕКТА:
    python scripts/seed_sources.py

Скрипт идемпотентный: если источник с таким URL уже есть, он его пропустит,
поэтому можно запускать несколько раз без последствий.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.database import SessionLocal, engine, Base
from app.models import Source


# Эти RSS-фиды проверены и работают на 2026 год.
SOURCES = [
    {"type": "site", "name": "Коммерсант",   "url": "https://www.kommersant.ru/RSS/news.xml",                     "enabled": True},
    {"type": "site", "name": "Лента.ру",     "url": "https://lenta.ru/rss/news",                                  "enabled": True},
    {"type": "site", "name": "ТАСС",         "url": "https://tass.ru/rss/v2.xml",                                 "enabled": True},
    {"type": "site", "name": "РИА Новости",  "url": "https://ria.ru/export/rss2/archive/index.xml",               "enabled": True},
    {"type": "site", "name": "РБК",          "url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",          "enabled": True},
    {"type": "site", "name": "Хабр (всё)",   "url": "https://habr.com/ru/rss/all/all/",                           "enabled": True},
]


def main():
    # На всякий случай создаём таблицы, если их ещё нет
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        added = 0
        skipped = 0
        for src in SOURCES:
            existing = db.query(Source).filter(Source.url == src["url"]).first()
            if existing:
                print(f"  ПРОПУСК: {src['name']} (уже есть, id={existing.id})")
                skipped += 1
                continue
            obj = Source(**src)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            print(f"  ДОБАВЛЕН: {src['name']} (id={obj.id})")
            added += 1
        print()
        print(f"Готово. Добавлено: {added}, пропущено: {skipped}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

"""
Общая логика парсинга: пройти по всем включённым источникам, вызвать нужный парсер,
сохранить новости в базу с защитой от дублей.
"""
from typing import Dict
from sqlalchemy.orm import Session

from app.models import Source, NewsItem
from app.news_parser.sites import parse_site
from app.news_parser.telegram import parse_telegram_channel


def _is_duplicate(db: Session, item: dict) -> bool:
    """
    Защита от дублей.
    Для сайтов проверяем по url (он уникален у нормальных сайтов).
    Для Telegram (url может быть None у заглушек) — по связке source + title.
    """
    if item.get("url"):
        existing = db.query(NewsItem).filter(NewsItem.url == item["url"]).first()
        if existing:
            return True

    existing = db.query(NewsItem).filter(
        NewsItem.source == item.get("source"),
        NewsItem.title == item.get("title"),
    ).first()
    return existing is not None


def run_parsing(db: Session) -> Dict[str, int]:
    """
    Главная функция парсинга.
    1. Берёт все включённые источники.
    2. Для каждого вызывает нужный парсер.
    3. Сохраняет новости, пропуская дубли.
    4. Возвращает статистику.
    """
    sources = db.query(Source).filter(Source.enabled.is_(True)).all()

    stats = {
        "sources_processed": 0,
        "items_found": 0,
        "items_saved": 0,
        "duplicates_skipped": 0,
        "errors": 0,
    }

    for src in sources:
        stats["sources_processed"] += 1
        try:
            if src.type == "site":
                items = parse_site(src.url, src.name)
            elif src.type == "tg":
                items = parse_telegram_channel(src.url, src.name)
            else:
                # неизвестный тип источника — пропускаем
                continue

            stats["items_found"] += len(items)

            for item in items:
                if _is_duplicate(db, item):
                    stats["duplicates_skipped"] += 1
                    continue
                db.add(NewsItem(**item))
                stats["items_saved"] += 1

            db.commit()
        except Exception as e:
            db.rollback()
            stats["errors"] += 1
            # для учебного проекта просто печатаем в консоль
            print(f"[parser] Ошибка при обработке источника {src.name}: {e}")

    return stats

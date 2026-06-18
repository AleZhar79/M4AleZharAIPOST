"""
Парсер новостей с сайтов через RSS.

Почему RSS, а не HTML:
- RSS — стандартный формат, его поддерживают почти все новостные сайты.
- Для HTML нужно писать отдельный парсер под верстку каждого сайта.
- Для учебного проекта RSS — самый простой и надёжный путь.

Если у сайта нет RSS — добавишь его HTML-парсер отдельно, когда дойдут руки.
"""
from datetime import datetime
from typing import List, Dict, Any

import feedparser


def parse_site(url: str, source_name: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Принимает URL RSS-фида и возвращает список новостей.
    Каждая новость — словарь, готовый к сохранению в NewsItem.
    """
    feed = feedparser.parse(url)
    items = []

    for entry in feed.entries[:limit]:
        # У RSS-фидов поле даты может называться по-разному, берём что есть
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published = datetime(*entry.updated_parsed[:6])
        else:
            published = datetime.utcnow()

        items.append({
            "title": getattr(entry, "title", "Без заголовка")[:500],
            "url": getattr(entry, "link", None),
            "summary": getattr(entry, "summary", "")[:2000] if hasattr(entry, "summary") else "",
            "source": source_name,
            "published_at": published,
            "raw_text": None,
        })

    return items

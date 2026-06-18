from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Source(Base):
    """Источник новостей: сайт или Telegram-канал."""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10), nullable=False)  # "site" или "tg"
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)  # URL сайта или @username канала
    enabled = Column(Boolean, default=True, nullable=False)


class Keyword(Base):
    """Ключевое слово для фильтрации новостей."""
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), unique=True, nullable=False, index=True)


class NewsItem(Base):
    """Сырая новость, собранная парсером (нужна для Блока 2, но создаём таблицу сразу)."""
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    raw_text = Column(Text, nullable=True)

    posts = relationship("Post", back_populates="news_item")


class Post(Base):
    """Сгенерированный AI пост для публикации в Telegram."""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news_items.id"), nullable=True)
    generated_text = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="new", nullable=False)  # new/generated/published/failed

    news_item = relationship("NewsItem", back_populates="posts")

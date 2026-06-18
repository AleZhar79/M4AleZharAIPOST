from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Для SQLite нужен флаг check_same_thread=False, потому что FastAPI работает с несколькими потоками
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Зависимость FastAPI: на каждый запрос — новая сессия, в конце закрываем."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

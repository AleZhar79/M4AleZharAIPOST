from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.database import Base, engine

# Создаём таблицы при старте (для учебного проекта — самый простой путь, без Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Telegram Bot",
    description="Сервис генерации постов в Telegram на основе новостей",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api")


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "docs": "/docs"}

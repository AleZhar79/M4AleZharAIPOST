from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Keyword, NewsItem, Post, Source
from app.api import schemas
from app.news_parser.service import run_parsing
from app.ai.generator import generate_post_text
from app.ai.openai_client import AIGenerationError
from app.telegram.publisher import publish_post as publisher_publish_post

router = APIRouter()


# ==================== SOURCES ====================
@router.post("/sources/", response_model=schemas.SourceOut, status_code=status.HTTP_201_CREATED, tags=["sources"])
def create_source(data: schemas.SourceCreate, db: Session = Depends(get_db)):
    obj = Source(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/sources/", response_model=List[schemas.SourceOut], tags=["sources"])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).all()


@router.get("/sources/{source_id}", response_model=schemas.SourceOut, tags=["sources"])
def get_source(source_id: int, db: Session = Depends(get_db)):
    obj = db.query(Source).get(source_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Source not found")
    return obj


@router.patch("/sources/{source_id}", response_model=schemas.SourceOut, tags=["sources"])
def update_source(source_id: int, data: schemas.SourceUpdate, db: Session = Depends(get_db)):
    obj = db.query(Source).get(source_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Source not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["sources"])
def delete_source(source_id: int, db: Session = Depends(get_db)):
    obj = db.query(Source).get(source_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(obj)
    db.commit()
    return None


# ==================== KEYWORDS ====================
@router.post("/keywords/", response_model=schemas.KeywordOut, status_code=status.HTTP_201_CREATED, tags=["keywords"])
def create_keyword(data: schemas.KeywordCreate, db: Session = Depends(get_db)):
    if db.query(Keyword).filter(Keyword.word == data.word).first():
        raise HTTPException(status_code=400, detail="Keyword already exists")
    obj = Keyword(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/keywords/", response_model=List[schemas.KeywordOut], tags=["keywords"])
def list_keywords(db: Session = Depends(get_db)):
    return db.query(Keyword).all()


@router.get("/keywords/{keyword_id}", response_model=schemas.KeywordOut, tags=["keywords"])
def get_keyword(keyword_id: int, db: Session = Depends(get_db)):
    obj = db.query(Keyword).get(keyword_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return obj


@router.patch("/keywords/{keyword_id}", response_model=schemas.KeywordOut, tags=["keywords"])
def update_keyword(keyword_id: int, data: schemas.KeywordUpdate, db: Session = Depends(get_db)):
    obj = db.query(Keyword).get(keyword_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Keyword not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/keywords/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["keywords"])
def delete_keyword(keyword_id: int, db: Session = Depends(get_db)):
    obj = db.query(Keyword).get(keyword_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(obj)
    db.commit()
    return None


# ==================== POSTS ====================
@router.post("/posts/", response_model=schemas.PostOut, status_code=status.HTTP_201_CREATED, tags=["posts"])
def create_post(data: schemas.PostCreate, db: Session = Depends(get_db)):
    obj = Post(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/posts/", response_model=List[schemas.PostOut], tags=["posts"])
def list_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()


@router.get("/posts/{post_id}", response_model=schemas.PostOut, tags=["posts"])
def get_post(post_id: int, db: Session = Depends(get_db)):
    obj = db.query(Post).get(post_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Post not found")
    return obj


@router.patch("/posts/{post_id}", response_model=schemas.PostOut, tags=["posts"])
def update_post(post_id: int, data: schemas.PostUpdate, db: Session = Depends(get_db)):
    obj = db.query(Post).get(post_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Post not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["posts"])
def delete_post(post_id: int, db: Session = Depends(get_db)):
    obj = db.query(Post).get(post_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(obj)
    db.commit()
    return None


# ==================== NEWS (read-only) ====================
@router.get("/news/", response_model=List[schemas.NewsItemOut], tags=["news"])
def list_news(limit: int = 50, db: Session = Depends(get_db)):
    return (
        db.query(NewsItem)
        .order_by(NewsItem.published_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/news/{news_id}", response_model=schemas.NewsItemOut, tags=["news"])
def get_news(news_id: int, db: Session = Depends(get_db)):
    obj = db.query(NewsItem).get(news_id)
    if not obj:
        raise HTTPException(status_code=404, detail="News not found")
    return obj


# ==================== PARSING ====================
@router.post("/parse/run", response_model=schemas.ParseResult, tags=["parser"])
def parse_now(db: Session = Depends(get_db)):
    """Парсинг синхронно в процессе FastAPI. Только для отладки."""
    return run_parsing(db)


@router.post("/parse/run-async", response_model=schemas.TaskScheduled, tags=["parser"])
def parse_async():
    """Кладёт парсинг в очередь Celery, возвращает task_id."""
    from app.tasks import parse_all_sources_task
    async_result = parse_all_sources_task.apply_async()
    return schemas.TaskScheduled(task_id=async_result.id)


@router.get("/tasks/{task_id}", response_model=schemas.TaskStatus, tags=["parser"])
def task_status(task_id: str):
    """Статус Celery-таска: PENDING / STARTED / SUCCESS / FAILURE."""
    from celery_worker import celery_app
    async_result = celery_app.AsyncResult(task_id)
    result = None
    if async_result.ready():
        try:
            result = async_result.result
            if not isinstance(result, dict):
                result = {"value": str(result)}
        except Exception as e:
            result = {"error": str(e)}
    return schemas.TaskStatus(task_id=task_id, state=async_result.state, result=result)


# ==================== AI GENERATION (Блок 4) ====================
@router.post("/generate/{news_id}", response_model=schemas.PostOut, tags=["generate"])
def generate_for_news(news_id: int, db: Session = Depends(get_db)):
    """
    Синхронная генерация: дёргает OpenRouter прямо в HTTP-запросе.
    Удобно для отладки промпта, НО запрос будет висеть 5–30 секунд.
    Для прода используй /api/generate/run-async/{news_id}.
    """
    news = db.query(NewsItem).get(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    try:
        text = generate_post_text(news)
    except AIGenerationError as e:
        # 502 — "сторонний сервис нас подвёл"
        raise HTTPException(status_code=502, detail=str(e))

    post = Post(news_id=news.id, generated_text=text, status="generated")
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.post("/generate/run-async/{news_id}", response_model=schemas.TaskScheduled, tags=["generate"])
def generate_async(news_id: int, db: Session = Depends(get_db)):
    """
    Асинхронная генерация: кладёт задачу в Celery и сразу возвращает task_id.
    Реальный результат — через GET /api/tasks/{task_id}.
    """
    # Проверяем, что новость существует — лучше вернуть 404 сразу,
    # чем уже из воркера логом.
    news = db.query(NewsItem).get(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    from app.tasks import generate_post_task
    async_result = generate_post_task.apply_async(args=[news_id])
    return schemas.TaskScheduled(task_id=async_result.id)


# ==================== PUBLISH (Блок 5, mock) ====================
@router.post("/publish/{post_id}", response_model=schemas.PostOut, tags=["publish"])
def publish_post_endpoint(post_id: int, db: Session = Depends(get_db)):
    """Mock — будет заменено в Блоке 5."""
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    publisher_publish_post(db, post)
    db.refresh(post)
    return post

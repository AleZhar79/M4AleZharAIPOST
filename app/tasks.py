"""
Celery-таски проекта.

Главная мысль: Celery — это просто способ запустить обычную функцию в фоне.
Бизнес-логика живёт в app/news_parser/, app/ai/ и app/telegram/, а тут только обёртки.
"""
from celery_worker import celery_app
from app.database import SessionLocal
from app.models import NewsItem, Post
from app.news_parser.service import run_parsing
from app.ai.generator import generate_post_text
from app.ai.openai_client import AIGenerationError
from app.telegram.publisher import publish_post
from app.utils import get_logger

log = get_logger(__name__)


@celery_app.task(name="app.tasks.parse_all_sources_task")
def parse_all_sources_task() -> dict:
    """
    Парсинг всех включённых источников.
    Запускается вручную через /api/parse/run-async и автоматически Beat'ом каждые 30 мин.
    """
    log.info("[celery] parse_all_sources_task: старт")
    db = SessionLocal()
    try:
        stats = run_parsing(db)
        log.info(f"[celery] parse_all_sources_task: готово, stats={stats}")
        return stats
    finally:
        db.close()


@celery_app.task(name="app.tasks.generate_post_task")
def generate_post_task(news_id: int) -> dict:
    """
    Генерация поста по новости через AI.
    Создаёт запись Post со status='generated' (или 'failed' при ошибке).
    """
    log.info(f"[celery] generate_post_task(news_id={news_id}): старт")
    db = SessionLocal()
    try:
        news = db.query(NewsItem).get(news_id)
        if not news:
            log.warning(f"[celery] generate_post_task: news_id={news_id} не найдена")
            return {"status": "not_found", "news_id": news_id}

        try:
            text = generate_post_text(news)
        except AIGenerationError as e:
            post = Post(news_id=news.id, generated_text=f"[FAILED] {e}", status="failed")
            db.add(post)
            db.commit()
            db.refresh(post)
            log.error(f"[celery] generate_post_task: ошибка AI — {e}")
            return {"status": "failed", "post_id": post.id, "error": str(e)}

        post = Post(news_id=news.id, generated_text=text, status="generated")
        db.add(post)
        db.commit()
        db.refresh(post)
        log.info(f"[celery] generate_post_task: пост {post.id} создан")
        return {"status": "generated", "post_id": post.id, "length": len(text)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.publish_post_task")
def publish_post_task(post_id: int) -> dict:
    """
    Публикация одного поста в Telegram-канал.

    Авто-ретрай НЕ ставим: при FloodWaitError Telegram сам говорит сколько ждать,
    а на остальные ошибки лучше посмотреть глазами, чем тихо спамить ретраями.
    """
    log.info(f"[celery] publish_post_task(post_id={post_id}): старт")
    db = SessionLocal()
    try:
        post = db.query(Post).get(post_id)
        if not post:
            log.warning(f"[celery] publish_post_task: post_id={post_id} не найден")
            return {"status": "not_found", "post_id": post_id}

        ok = publish_post(db, post)
        return {
            "status": "published" if ok else "failed",
            "post_id": post.id,
            "post_status": post.status,
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.pipeline_task")
def pipeline_task() -> dict:
    """
    Полная цепочка: парсинг → генерация по каждой новой новости → публикация.

    Делаем ПРОСТО, без orchestrate/chord. Учебный проект — последовательно
    в одной задаче. На несколько сотен новостей это вполне нормально.
    """
    log.info("[celery] pipeline_task: старт")
    db = SessionLocal()
    try:
        stats = run_parsing(db)
        log.info(f"[celery] pipeline_task: парсинг готов, stats={stats}")

        # Берём только что добавленные новости, которым ещё не сделали пост.
        # Узнаём это запросом — у NewsItem нет прямого "uses_in_post" поля,
        # поэтому проще: ищем NewsItem без связанных Post.
        from sqlalchemy import select, not_, exists
        news_without_post = (
            db.query(NewsItem)
            .filter(not_(exists().where(Post.news_id == NewsItem.id)))
            .order_by(NewsItem.published_at.desc())
            .limit(5)            # за раз обрабатываем максимум 5, чтобы не упереться в rate limit
            .all()
        )
        log.info(f"[celery] pipeline_task: новых новостей для генерации: {len(news_without_post)}")

        generated = 0
        published = 0
        failed = 0

        for news in news_without_post:
            try:
                text = generate_post_text(news)
                post = Post(news_id=news.id, generated_text=text, status="generated")
                db.add(post)
                db.commit()
                db.refresh(post)
                generated += 1

                ok = publish_post(db, post)
                if ok:
                    published += 1
                else:
                    failed += 1
            except AIGenerationError as e:
                log.error(f"[celery] pipeline_task: AI ошибка для news_id={news.id}: {e}")
                post = Post(news_id=news.id, generated_text=f"[FAILED] {e}", status="failed")
                db.add(post)
                db.commit()
                failed += 1
            except Exception as e:
                log.error(f"[celery] pipeline_task: неожиданная ошибка для news_id={news.id}: {e}")
                failed += 1

        result = {
            "parse": stats,
            "generated": generated,
            "published": published,
            "failed": failed,
        }
        log.info(f"[celery] pipeline_task: готово, result={result}")
        return result
    finally:
        db.close()

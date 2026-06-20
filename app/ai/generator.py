"""
БЛОК 4 — генератор постов.

Собирает промпт из новости, дёргает OpenAI-клиент и возвращает текст поста.
При ошибке генерации пробрасывает AIGenerationError наверх.
"""
from app.ai.openai_client import call_openai, AIGenerationError  # noqa: F401  (реэкспорт)
from app.models import NewsItem
from app.utils import get_logger

log = get_logger(__name__)


PROMPT_TEMPLATE = """Ты — редактор Telegram-канала.
Сделай из этой новости короткий, яркий пост для канала.
Требования:
- 3–6 предложений
- добавь подходящие emoji
- в конце добавь call to action (подписка/комментарий)
- пиши на том же языке, что и исходная новость
- НЕ придумывай факты, которых нет в исходной новости

Исходная новость:
Заголовок: {title}
Источник: {source}
Краткое содержание: {summary}
"""


def build_prompt(news: NewsItem) -> str:
    """Собирает промпт для генерации поста из объекта новости."""
    return PROMPT_TEMPLATE.format(
        title=news.title or "",
        source=news.source or "",
        summary=(news.summary or news.raw_text or "")[:1500],
    )


def generate_post_text(news: NewsItem) -> str:
    """
    Главная функция: из новости делает текст поста.
    Может бросить AIGenerationError, если что-то пошло не так с AI.
    """
    log.info(f"[generator] генерирую пост для news_id={news.id}, title={news.title!r}")
    prompt = build_prompt(news)
    return call_openai(prompt)

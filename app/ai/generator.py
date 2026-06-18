"""
БЛОК 4 — генератор постов (СКЕЛЕТ).

Отвечает за то, чтобы из NewsItem собрать промпт, дёрнуть OpenAI
и вернуть готовый текст поста.

Это уже почти рабочая логика — потому что промпт и сборка ввода
не зависят от того, реальный у нас OpenAI или mock.
В Блоке 4 будем только улучшать промпт и обрабатывать ошибки API.
"""
from app.ai.openai_client import call_openai
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
    Сейчас под капотом mock OpenAI, в Блоке 4 заменим на реальный API.
    """
    log.info(f"[generator] генерирую пост для news_id={news.id}, title={news.title!r}")
    prompt = build_prompt(news)
    return call_openai(prompt)

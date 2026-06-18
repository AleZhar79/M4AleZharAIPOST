"""
Общие утилиты. Пока тут только настройка логгера.
"""
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает логгер с единым форматом для всего проекта.
    Использование:
        from app.utils import get_logger
        log = get_logger(__name__)
        log.info("сообщение")
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

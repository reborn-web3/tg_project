"""Утилита для работы с текстовыми шаблонами"""
from typing import Optional
from database import async_session_maker, TextTemplateRepository


async def get_text(key: str, default: str = "") -> str:
    """
    Получить текст по ключу из БД.
    Если текст не найден, возвращает default.
    """
    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        template = await repo.get_by_key(key)
        return template.content if template else default


async def get_all_texts() -> dict[str, str]:
    """Получить все тексты в виде словаря {key: content}"""
    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        templates = await repo.get_all()
        return {t.key: t.content for t in templates}


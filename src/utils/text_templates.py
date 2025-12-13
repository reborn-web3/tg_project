"""
Утилита для работы с текстовыми шаблонами из БД
"""

from typing import Optional
from database import async_session_maker, TextTemplateRepository


async def get_text_template(key: str, **format_kwargs) -> str:
    """
    Получить текст шаблона из БД и отформатировать его.

    Args:
        key: Ключ шаблона (например, 'welcome_new')
        **format_kwargs: Параметры для форматирования (first_name, city и т.д.)

    Returns:
        Отформатированный текст шаблона
    """
    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        template = await repo.get_by_key(key)

        if not template:
            # Если шаблон не найден, возвращаем дефолтный текст
            return f"⚠️ Текст '{key}' не найден в базе данных."

        try:
            # Форматируем текст с переданными параметрами
            return template.content.format(**format_kwargs)
        except KeyError as e:
            # Если не хватает параметров для форматирования
            return template.content


async def get_text_or_default(key: str, default: str, **format_kwargs) -> str:
    """
    Получить текст из БД или вернуть дефолтный, если не найден.

    Args:
        key: Ключ шаблона
        default: Дефолтный текст, если шаблон не найден
        **format_kwargs: Параметры для форматирования

    Returns:
        Текст шаблона или дефолтный текст
    """
    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        template = await repo.get_by_key(key)

        if not template:
            return default.format(**format_kwargs) if format_kwargs else default

        try:
            return template.content.format(**format_kwargs)
        except KeyError:
            return template.content

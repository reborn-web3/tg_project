import re
from typing import Optional


class ValidationError(Exception):
    """Ошибка валидации данных"""

    pass


def validate_full_name(text: str) -> tuple[str, str]:
    """
    Валидация имени и фамилии.

    Args:
        text: Строка с именем и фамилией

    Returns:
        tuple: (first_name, last_name)

    Raises:
        ValidationError: Если данные не прошли валидацию
    """
    # Убираем лишние пробелы
    text = " ".join(text.split())

    # Проверяем что введено минимум 2 слова
    parts = text.split()
    if len(parts) < 2:
        raise ValidationError(
            "❌ Пожалуйста, введите имя и фамилию (минимум 2 слова).\n"
            "Например: Иван Иванов"
        )

    # Проверяем что слова содержат только буквы (поддержка кириллицы и латиницы)
    if not all(re.match(r"^[а-яёА-ЯЁa-zA-Z-]+$", part) for part in parts):
        raise ValidationError(
            "❌ Имя и фамилия должны содержать только буквы.\nНапример: Иван Иванов"
        )

    # Проверяем минимальную длину
    if any(len(part) < 2 for part in parts):
        raise ValidationError(
            "❌ Имя и фамилия должны содержать минимум 2 буквы каждое."
        )

    # Берем первые два слова и капитализируем
    first_name = parts[0].capitalize()
    last_name = parts[1].capitalize()

    return first_name, last_name


def validate_city(text: str) -> str:
    """
    Валидация названия города.

    Args:
        text: Название города

    Returns:
        str: Валидированное название города

    Raises:
        ValidationError: Если данные не прошли валидацию
    """
    # Убираем лишние пробелы
    text = " ".join(text.split())

    # Проверяем минимальную длину
    if len(text) < 2:
        raise ValidationError(
            "❌ Название города слишком короткое.\n"
            "Пожалуйста, введите корректное название."
        )

    # Проверяем максимальную длину
    if len(text) > 100:
        raise ValidationError(
            "❌ Название города слишком длинное (максимум 100 символов)."
        )

    # Проверяем что содержит в основном буквы
    if not re.search(r"[а-яёА-ЯЁa-zA-Z]", text):
        raise ValidationError(
            "❌ Название города должно содержать буквы.\n"
            "Например: Москва, Санкт-Петербург"
        )

    # Капитализируем первую букву каждого слова
    return text.title()


def validate_about(text: str) -> Optional[str]:
    """
    Валидация текста "О себе".

    Args:
        text: Текст о себе

    Returns:
        str: Валидированный текст или None если пусто

    Raises:
        ValidationError: Если данные не прошли валидацию
    """
    # Убираем лишние пробелы
    text = " ".join(text.split())

    # Если текст пустой, возвращаем None
    if not text:
        return None

    # Проверяем минимальную длину
    if len(text) < 10:
        raise ValidationError(
            "❌ Описание слишком короткое.\n"
            "Расскажите о себе немного подробнее (минимум 10 символов)."
        )

    # Подсчитываем количество слов
    words = text.split()
    if len(words) > 150:
        raise ValidationError(
            f"❌ Описание слишком длинное ({len(words)} слов).\n"
            "Максимум 150 слов. Пожалуйста, сократите текст."
        )

    return text


def get_interest_names() -> dict[str, str]:
    """Получить маппинг callback_data -> название интереса"""
    return {
        "interest_investments": "Инвестиции",
        "interest_career": "Карьерное развитие",
        "interest_business": "Предпринимательство и бизнес",
        "interest_economy": "Экономика",
        "interest_marketing": "Маркетинг",
        "interest_art": "Искусство",
        "interest_sport": "Спорт",
    }


def get_event_names() -> dict[str, str]:
    """Получить маппинг callback_data -> название типа мероприятия"""
    return {
        "event_business": "Деловые",
        "event_educational": "Обучающие",
        "event_sport": "Спортивные",
        "event_cultural": "Культурные",
        "event_gastronomic": "Гастрономические",
    }

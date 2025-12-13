from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню админ-панели"""
    keyboard = [
        [InlineKeyboardButton(text="📝 Редактировать тексты", callback_data="admin_edit_texts")],
        [InlineKeyboardButton(text="📋 Список всех текстов", callback_data="admin_list_texts")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_close")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_text_list_keyboard(texts: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком текстов для редактирования.
    texts: список кортежей (key, title)
    """
    keyboard = []
    for key, title in texts:
        # Ограничиваем длину названия для красоты
        display_title = title[:40] + "..." if len(title) > 40 else title
        keyboard.append(
            [InlineKeyboardButton(text=f"✏️ {display_title}", callback_data=f"admin_edit_{key}")]
        )
    
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_text_edit_keyboard(key: str) -> InlineKeyboardMarkup:
    """Клавиатура для редактирования конкретного текста"""
    keyboard = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"admin_edit_content_{key}")],
        [InlineKeyboardButton(text="👁️ Просмотреть", callback_data=f"admin_view_{key}")],
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data="admin_edit_texts")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    keyboard = [[InlineKeyboardButton(text="❌ Отменить", callback_data="admin_cancel_edit")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from config import settings
from states.admin import AdminStates
from database import async_session_maker, TextTemplateRepository
from database.init_texts import TEXT_KEYS, init_default_texts
from keyboards.admin import (
    get_admin_main_keyboard,
    get_text_list_keyboard,
    get_text_edit_keyboard,
    get_cancel_keyboard,
)

admin_router = Router()


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь админом"""
    return user_id == settings.ADMIN_USER_ID


@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Команда для входа в админ-панель"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    await state.set_state(AdminStates.main_menu)
    await message.answer(
        "👑 <b>Админ-панель</b>\n\nВыберите действие:",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML",
    )


@admin_router.callback_query(
    StateFilter(AdminStates.main_menu, AdminStates.editing_text),
    F.data == "admin_close",
)
async def close_admin(callback: CallbackQuery, state: FSMContext):
    """Закрытие админ-панели"""
    await callback.answer()  # КРИТИЧНО: всегда первым!
    await state.clear()
    await callback.message.edit_text("Админ-панель закрыта.")


@admin_router.callback_query(
    StateFilter(AdminStates.main_menu, AdminStates.editing_text),
    F.data == "admin_back_to_main",
)
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await callback.answer()  # КРИТИЧНО!
    await state.set_state(AdminStates.main_menu)
    await callback.message.edit_text(
        "👑 <b>Админ-панель</b>\n\nВыберите действие:",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML",
    )


@admin_router.callback_query(
    StateFilter(AdminStates.main_menu, AdminStates.editing_text),
    F.data == "admin_edit_texts",
)
async def show_text_list(callback: CallbackQuery, state: FSMContext):
    """Показать список текстов для редактирования"""
    await callback.answer()  # КРИТИЧНО!

    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        templates = await repo.get_all()

        # Создаем список из ключей, которые определены в TEXT_KEYS
        text_list = []
        template_dict = {t.key: t for t in templates}

        # Добавляем тексты из TEXT_KEYS, если они есть в БД
        for key, (title, _) in TEXT_KEYS.items():
            if key in template_dict:
                text_list.append((key, title))

        # Инициализируем тексты по умолчанию, если их еще нет
        if not text_list:
            await init_default_texts()
            templates = await repo.get_all()
            template_dict = {t.key: t for t in templates}
            for key, (title, _) in TEXT_KEYS.items():
                if key in template_dict:
                    text_list.append((key, title))

    await state.set_state(AdminStates.editing_text)
    await callback.message.edit_text(
        "📝 <b>Выберите текст для редактирования:</b>",
        reply_markup=get_text_list_keyboard(text_list),
        parse_mode="HTML",
    )


@admin_router.callback_query(
    StateFilter(AdminStates.main_menu, AdminStates.editing_text),
    F.data == "admin_list_texts",
)
async def list_all_texts(callback: CallbackQuery):
    """Показать список всех текстов с их содержимым"""
    # 🔴 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: await callback.answer() ПЕРВЫМ!
    await callback.answer()

    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        templates = await repo.get_all()

    if not templates:
        await callback.message.answer(
            "📋 Тексты не найдены.\nИспользуйте 'Редактировать тексты' для создания.",
            parse_mode="HTML",
        )
        return

    text_lines = ["📋 <b>Все тексты:</b>\n"]
    for template in templates[:20]:  # Ограничиваем до 20 для читаемости
        content_preview = (
            template.content[:50] + "..."
            if len(template.content) > 50
            else template.content
        )
        text_lines.append(
            f"<b>{template.title}</b> ({template.key}):\n{content_preview}\n"
        )

    text = "\n".join(text_lines)
    if len(templates) > 20:
        text += f"\n... и еще {len(templates) - 20} текстов"

    # Используем answer вместо edit, чтобы не конфликтовать с главным меню
    await callback.message.answer(text, parse_mode="HTML")


@admin_router.callback_query(
    StateFilter(AdminStates.editing_text), F.data.startswith("admin_view_")
)
async def view_text(callback: CallbackQuery):
    """Просмотр полного текста"""
    await callback.answer()  # КРИТИЧНО!

    key = callback.data.replace("admin_view_", "")

    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        template = await repo.get_by_key(key)

    if not template:
        await callback.answer("Текст не найден!", show_alert=True)
        return

    text = (
        f"👁️ <b>{template.title}</b> ({key})\n\n"
        f"<b>Содержимое:</b>\n{template.content}\n\n"
        f"<b>Описание:</b> {template.description or 'Нет описания'}"
    )

    await callback.message.answer(text, parse_mode="HTML")


@admin_router.callback_query(
    StateFilter(AdminStates.editing_text), F.data.startswith("admin_edit_content_")
)
async def start_edit_content(callback: CallbackQuery, state: FSMContext):
    """Начало редактирования содержимого текста"""
    await callback.answer()  # КРИТИЧНО!

    key = callback.data.replace("admin_edit_content_", "")

    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        template = await repo.get_by_key(key)

    if not template:
        await callback.answer("Текст не найден!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_new_content)
    await state.update_data(editing_key=key, editing_title=template.title)

    await callback.message.edit_text(
        f"✏️ <b>Редактирование: {template.title}</b>\n\n"
        f"<b>Текущий текст:</b>\n<code>{template.content}</code>\n\n"
        f"📝 Отправьте новый текст (поддерживается HTML):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )


@admin_router.callback_query(
    StateFilter(AdminStates.editing_text), F.data.startswith("admin_edit_")
)
async def edit_text_select(callback: CallbackQuery, state: FSMContext):
    """Выбор текста для редактирования"""
    await callback.answer()  # КРИТИЧНО!

    key = callback.data.replace("admin_edit_", "")

    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        template = await repo.get_by_key(key)

    if not template:
        await callback.answer("Текст не найден!", show_alert=True)
        return

    # Показываем текущий текст и предлагаем редактировать
    preview = (
        template.content[:200] + "..."
        if len(template.content) > 200
        else template.content
    )
    text = (
        f"📝 <b>{template.title}</b>\n\n"
        f"<b>Текущий текст:</b>\n"
        f"<code>{preview}</code>\n\n"
        f"Описание: {template.description or 'Нет описания'}"
    )

    await state.update_data(editing_key=key)
    await callback.message.edit_text(
        text,
        reply_markup=get_text_edit_keyboard(key),
        parse_mode="HTML",
    )


@admin_router.callback_query(
    StateFilter(AdminStates.waiting_for_new_content), F.data == "admin_cancel_edit"
)
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    """Отмена редактирования"""
    await callback.answer()  # КРИТИЧНО!

    await state.set_state(AdminStates.editing_text)

    # Получаем список текстов
    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        templates = await repo.get_all()
        template_dict = {t.key: t for t in templates}
        text_list = [
            (key, title)
            for key, (title, _) in TEXT_KEYS.items()
            if key in template_dict
        ]

    await callback.message.edit_text(
        "📝 <b>Редактирование отменено.</b>\n\nВыберите текст для редактирования:",
        reply_markup=get_text_list_keyboard(text_list),
        parse_mode="HTML",
    )


@admin_router.message(StateFilter(AdminStates.waiting_for_new_content))
async def save_new_content(message: Message, state: FSMContext):
    """Сохранение нового содержимого текста"""
    data = await state.get_data()
    key = data.get("editing_key")
    title = data.get("editing_title")

    if not key:
        await message.answer("❌ Ошибка: ключ текста не найден.")
        await state.clear()
        return

    new_content = message.text

    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        template = await repo.get_by_key(key)
        if template:
            await repo.create_or_update(key, title, new_content, template.description)
        else:
            # Если шаблона нет, создаем его
            description = TEXT_KEYS.get(key, ("", ""))[1]
            await repo.create_or_update(key, title, new_content, description)

    await state.set_state(AdminStates.editing_text)
    await message.answer(
        f"✅ <b>Текст успешно обновлен!</b>\n\n"
        f"<b>Новый текст:</b>\n<code>{new_content[:200]}{'...' if len(new_content) > 200 else ''}</code>",
        parse_mode="HTML",
    )

    # Показываем меню выбора текстов
    async with async_session_maker() as session:
        repo = TextTemplateRepository(session)
        templates = await repo.get_all()
        template_dict = {t.key: t for t in templates}
        text_list = [
            (key, title)
            for key, (title, _) in TEXT_KEYS.items()
            if key in template_dict
        ]

    await message.answer(
        "📝 <b>Выберите текст для редактирования:</b>",
        reply_markup=get_text_list_keyboard(text_list),
        parse_mode="HTML",
    )

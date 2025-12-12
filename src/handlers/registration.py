from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from states.registration import RegistrationStates
from database import async_session_maker, UserRepository
from keyboards.registration import (
    get_interests_keyboard,
    get_events_keyboard,
    get_skip_keyboard,
    update_interests_keyboard,
    update_events_keyboard,
    get_edit_profile_keyboard,
)
from utils.validators import (
    validate_full_name,
    validate_city,
    validate_about,
    ValidationError,
    get_interest_names,
    get_event_names,
)

registration_router = Router()

# Карта доступных чатов и их ссылок
CHAT_LINKS = {
    "investments": (
        "Чат инвестиций",
        "https://t.me/+hDOyTja5fJxjNTM6",
    ),
    "management": (
        "Чат менеджмента",
        "https://t.me/+3vE_6_mHzeA5NzY6",
    ),
    "marketing": (
        "Маркетинговый чат",
        "https://t.me/+IHrqutbfD-kyOTQ6",
    ),
}

# Соответствие выбранных сфер интересов рекомендуемым чатам
INTEREST_CHAT_MAP = {
    "interest_investments": ["investments"],
    "interest_career": ["management"],
    "interest_business": ["management"],
    "interest_economy": ["investments"],
    "interest_marketing": ["marketing"],
    "interest_art": ["marketing"],
    "interest_sport": [],
}

# Соответствие выбранных типов мероприятий рекомендуемым чатам
EVENT_CHAT_MAP = {
    "event_business": ["management"],
    "event_educational": [],
    "event_sport": [],
    "event_cultural": ["marketing"],
    "event_gastronomic": [],
}


from aiogram.types import LinkPreviewOptions


def _build_chat_recommendations(
    selected_interests: list[str] | None, selected_events: list[str] | None
) -> tuple[str, dict] | None:
    """
    Подбор списка чатов по выбранным интересам и типам мероприятий.
    Возвращает (HTML-текст, параметры) или None.
    """
    selected_interests = selected_interests or []
    selected_events = selected_events or []

    ordered_chats: list[str] = []
    seen = set()

    def _append_chats(keys: list[str]):
        for chat_key in keys:
            if chat_key not in seen:
                ordered_chats.append(chat_key)
                seen.add(chat_key)

    for interest in selected_interests:
        _append_chats(INTEREST_CHAT_MAP.get(interest, []))

    for event in selected_events:
        _append_chats(EVENT_CHAT_MAP.get(event, []))

    if not ordered_chats:
        return None

    lines = ["📌 Рекомендуем Вам присоединиться к следующим сообществам:"]
    for chat_key in ordered_chats:
        title, url = CHAT_LINKS[chat_key]
        lines.append(f'• <a href="{url}">{title}</a>')

    text = "\n".join(lines)
    return text, {"link_preview_options": LinkPreviewOptions(is_disabled=True)}


@registration_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Начало регистрации"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name_tg = message.from_user.first_name

    # Создаем или получаем пользователя
    async with async_session_maker() as session:
        repo = UserRepository(session)
        user, created = await repo.get_or_create(
            user_id=user_id, username=username, first_name_tg=first_name_tg
        )

        # Проверяем, заполнен ли профиль
        if user.first_name and user.city:
            await message.answer(
                f"👋 С возвращением, <b>{user.first_name}</b>!\n\n"
                f"Ваш профиль уже заполнен.\n"
                f"Используйте /profile чтобы посмотреть информацию.",
                parse_mode="HTML",
            )
            await state.clear()
            return

    # Начинаем регистрацию
    await message.answer(
        f"👋 Привет, <b>{first_name_tg}</b>!\n\n"
        f"Давайте познакомимся поближе.\n\n"
        f"<b>Как Вас зовут?</b>\n"
        f"Введите имя и фамилию.",
        parse_mode="HTML",
    )
    await state.set_state(RegistrationStates.waiting_for_name)


@registration_router.message(Command("edit"))
async def cmd_edit(message: Message, state: FSMContext):
    """Меню редактирования профиля"""
    user_id = message.from_user.id

    async with async_session_maker() as session:
        repo = UserRepository(session)
        user = await repo.get_by_id(user_id)

    if not user or not user.first_name:
        await message.answer(
            "❌ Профиль еще не заполнен.\nИспользуйте /start для регистрации.",
            parse_mode="HTML",
        )
        await state.clear()
        return

    await state.clear()
    await state.set_state(RegistrationStates.editing_menu)
    await message.answer(
        "Что хотите изменить?",
        reply_markup=get_edit_profile_keyboard(),
        parse_mode="HTML",
    )


@registration_router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка ввода имени и фамилии"""
    try:
        first_name, last_name = validate_full_name(message.text)

        # Сохраняем во временные данные состояния
        await state.update_data(first_name=first_name, last_name=last_name)

        # Переходим к следующему шагу
        await message.answer(
            f"✅ Отлично, <b>{first_name} {last_name}</b>!\n\n"
            f"<b>Из какого вы города?</b>",
            parse_mode="HTML",
        )
        await state.set_state(RegistrationStates.waiting_for_city)

    except ValidationError as e:
        await message.answer(str(e), parse_mode="HTML")


@registration_router.message(RegistrationStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    """Обработка ввода города"""
    try:
        city = validate_city(message.text)

        # Сохраняем город
        await state.update_data(city=city)

        # Переходим к выбору интересов
        await message.answer(
            f"✅ Город: <b>{city}</b>\n\n"
            f"<b>Какими сферами вы интересуетесь?</b>\n"
            f"Выберите один или несколько вариантов:",
            reply_markup=get_interests_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(RegistrationStates.waiting_for_interests)
        # Инициализируем список выбранных интересов
        await state.update_data(selected_interests=[])

    except ValidationError as e:
        await message.answer(str(e), parse_mode="HTML")


@registration_router.callback_query(
    RegistrationStates.waiting_for_interests, F.data.startswith("interest_")
)
async def process_interest_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора интересов"""
    data = await state.get_data()
    selected = data.get("selected_interests", [])

    # Переключаем выбор
    if callback.data in selected:
        selected.remove(callback.data)
    else:
        selected.append(callback.data)

    await state.update_data(selected_interests=selected)

    # Обновляем клавиатуру
    await callback.message.edit_reply_markup(
        reply_markup=update_interests_keyboard(selected)
    )
    await callback.answer()


@registration_router.callback_query(
    RegistrationStates.waiting_for_interests, F.data == "interests_confirm"
)
async def confirm_interests(callback: CallbackQuery, state: FSMContext):
    """Подтверждение выбора интересов"""
    data = await state.get_data()
    selected = data.get("selected_interests", [])

    if not selected:
        await callback.answer("❌ Выберите хотя бы один интерес!", show_alert=True)
        return

    # Получаем названия интересов
    interest_names = get_interest_names()
    selected_names = [interest_names[i] for i in selected]
    interests_str = ", ".join(selected_names)

    # Сохраняем в БД формат: через запятую
    await state.update_data(interests=interests_str)

    # Переходим к выбору типов мероприятий
    await callback.message.edit_text(
        f"✅ Интересы: <b>{interests_str}</b>", parse_mode="HTML"
    )

    await callback.message.answer(
        "<b>Какие мероприятия Вам интересны?</b>\n"
        "Выберите один или несколько вариантов:",
        reply_markup=get_events_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(RegistrationStates.waiting_for_events)
    await state.update_data(selected_events=[])
    await callback.answer()


@registration_router.callback_query(
    RegistrationStates.waiting_for_events, F.data.startswith("event_")
)
async def process_event_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типов мероприятий"""
    data = await state.get_data()
    selected = data.get("selected_events", [])

    # Переключаем выбор
    if callback.data in selected:
        selected.remove(callback.data)
    else:
        selected.append(callback.data)

    await state.update_data(selected_events=selected)

    # Обновляем клавиатуру
    await callback.message.edit_reply_markup(
        reply_markup=update_events_keyboard(selected)
    )
    await callback.answer()


@registration_router.callback_query(
    RegistrationStates.waiting_for_events, F.data == "events_confirm"
)
async def confirm_events(callback: CallbackQuery, state: FSMContext):
    """Подтверждение выбора типов мероприятий"""
    data = await state.get_data()
    selected = data.get("selected_events", [])

    if not selected:
        await callback.answer(
            "❌ Выберите хотя бы один тип мероприятий!", show_alert=True
        )
        return

    # Получаем названия типов мероприятий
    event_names = get_event_names()
    selected_names = [event_names[e] for e in selected]
    events_str = ", ".join(selected_names)

    # Сохраняем
    await state.update_data(events=events_str)

    # Переходим к описанию о себе
    await callback.message.edit_text(
        f"✅ Типы мероприятий: <b>{events_str}</b>", parse_mode="HTML"
    )

    await callback.message.answer(
        "<b>Расскажите о себе</b>\n\n"
        "Это поможет лучше подобрать для Вас собеседника.\n"
        "Максимум 150 слов.\n\n"
        "Или нажмите кнопку, чтобы пропустить этот шаг.",
        reply_markup=get_skip_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(RegistrationStates.waiting_for_about)
    await callback.answer()


@registration_router.message(RegistrationStates.waiting_for_about)
async def process_about(message: Message, state: FSMContext):
    """Обработка описания о себе"""
    try:
        about = validate_about(message.text)
        await state.update_data(about=about)
        await finalize_registration(message, state)

    except ValidationError as e:
        await message.answer(str(e), parse_mode="HTML")


@registration_router.callback_query(
    StateFilter(RegistrationStates.waiting_for_about, RegistrationStates.editing_about),
    F.data == "skip_about",
)
async def skip_about(callback: CallbackQuery, state: FSMContext):
    """Пропуск описания о себе"""
    current_state = await state.get_state()
    await state.update_data(about=None)
    await callback.message.delete()

    if current_state == RegistrationStates.editing_about.state:
        async with async_session_maker() as session:
            repo = UserRepository(session)
            await repo.update(user_id=callback.from_user.id, about=None)

        await state.set_state(RegistrationStates.editing_menu)
        await callback.message.answer(
            "О себе удалено. Что еще изменить?",
            reply_markup=get_edit_profile_keyboard(),
            parse_mode="HTML",
        )
    else:
        await finalize_registration(callback.message, state)

    await callback.answer()


async def finalize_registration(message: Message, state: FSMContext):
    """Завершение регистрации и сохранение в БД"""
    data = await state.get_data()
    user_id = message.from_user.id

    # Сохраняем все данные в БД
    async with async_session_maker() as session:
        repo = UserRepository(session)
        await repo.update(
            user_id=user_id,
            first_name=data["first_name"],
            last_name=data["last_name"],
            city=data["city"],
            interests=data["interests"],
            events=data["events"],
            about=data.get("about"),
        )

    # Отправляем поздравление со статусом Бриллиант
    await message.answer(
        f"{data['first_name']}, Поздравляем Вас с получением статуса Бриллиант 💎",
        parse_mode="HTML",
    )

    # Формируем итоговое сообщение
    about_text = data.get("about", "Не указано")
    summary = (
        "🎉 <b>Спасибо, что ответили!</b>\n\n"
        "<b>Ваши ответы:</b>\n\n"
        f"👤 <b>Имя:</b> {data['first_name']} {data['last_name']}\n"
        f"🏙️ <b>Город:</b> {data['city']}\n"
        f"💡 <b>Интересы:</b> {data['interests']}\n"
        f"🎪 <b>Мероприятия:</b> {data['events']}\n"
        f"📝 <b>О себе:</b> {about_text}\n\n"
        "Ваш профиль успешно создан! ✅"
    )

    await message.answer(summary, parse_mode="HTML")

    recommendations = _build_chat_recommendations(
        data.get("selected_interests"), data.get("selected_events")
    )
    if recommendations:
        text, kwargs = recommendations
        await message.answer(text, parse_mode="HTML", **kwargs)

    else:
        await message.answer(
            "Пока нет готовых рекомендаций по выбранным интересам. "
            "Мы дополним список чатов в ближайшее время!",
            parse_mode="HTML",
        )
    await state.clear()


@registration_router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Просмотр профиля пользователя"""
    user_id = message.from_user.id

    async with async_session_maker() as session:
        repo = UserRepository(session)
        user = await repo.get_by_id(user_id)

        if not user or not user.first_name:
            await message.answer(
                "❌ Профиль не заполнен.\nИспользуйте /start для регистрации."
            )
            return

        about_text = user.about or "Не указано"
        profile_text = (
            "📋 <b>Ваш профиль:</b>\n\n"
            f"👤 <b>Имя:</b> {user.first_name} {user.last_name or ''}\n"
            f"🏙️ <b>Город:</b> {user.city or 'Не указан'}\n"
            f"💡 <b>Интересы:</b> {user.interests or 'Не указаны'}\n"
            f"🎪 <b>Мероприятия:</b> {user.events or 'Не указаны'}\n"
            f"📝 <b>О себе:</b> {about_text}"
        )

        await message.answer(profile_text, parse_mode="HTML")


# ------------------- Редактирование профиля ------------------- #


@registration_router.callback_query(
    RegistrationStates.editing_menu, F.data == "edit_cancel"
)
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Редактирование отменено.")
    await callback.answer()


@registration_router.callback_query(
    RegistrationStates.editing_menu, F.data == "edit_name"
)
async def edit_name(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationStates.editing_name)
    await callback.message.edit_text(
        "<b>Введите имя и фамилию</b>\nНапример: Иван Иванов", parse_mode="HTML"
    )
    await callback.answer()


@registration_router.message(RegistrationStates.editing_name)
async def process_edit_name(message: Message, state: FSMContext):
    try:
        first_name, last_name = validate_full_name(message.text)
        async with async_session_maker() as session:
            repo = UserRepository(session)
            await repo.update(
                user_id=message.from_user.id,
                first_name=first_name,
                last_name=last_name,
            )
        await message.answer(
            f"✅ Имя обновлено: <b>{first_name} {last_name}</b>", parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.editing_menu)
        await message.answer(
            "Что еще изменить?",
            reply_markup=get_edit_profile_keyboard(),
            parse_mode="HTML",
        )
    except ValidationError as e:
        await message.answer(str(e), parse_mode="HTML")


@registration_router.callback_query(
    RegistrationStates.editing_menu, F.data == "edit_city"
)
async def edit_city(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationStates.editing_city)
    await callback.message.edit_text("<b>Из какого вы города?</b>", parse_mode="HTML")
    await callback.answer()


@registration_router.message(RegistrationStates.editing_city)
async def process_edit_city(message: Message, state: FSMContext):
    try:
        city = validate_city(message.text)
        async with async_session_maker() as session:
            repo = UserRepository(session)
            await repo.update(user_id=message.from_user.id, city=city)
        await message.answer(f"✅ Город обновлен: <b>{city}</b>", parse_mode="HTML")
        await state.set_state(RegistrationStates.editing_menu)
        await message.answer(
            "Что еще изменить?",
            reply_markup=get_edit_profile_keyboard(),
            parse_mode="HTML",
        )
    except ValidationError as e:
        await message.answer(str(e), parse_mode="HTML")


def _preselect_callbacks_from_names(
    raw_values: str | None, mapping: dict[str, str]
) -> list[str]:
    """Восстановить callback_data по сохраненным названиям (строка через запятую)"""
    if not raw_values:
        return []
    reverse = {name.lower(): key for key, name in mapping.items()}
    selected = []
    for item in raw_values.split(","):
        name = item.strip().lower()
        if name in reverse:
            selected.append(reverse[name])
    return selected


@registration_router.callback_query(
    RegistrationStates.editing_menu, F.data == "edit_interests"
)
async def edit_interests(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    async with async_session_maker() as session:
        repo = UserRepository(session)
        user = await repo.get_by_id(user_id)

    selected = (
        _preselect_callbacks_from_names(user.interests, get_interest_names())
        if user
        else []
    )

    await state.update_data(selected_interests=selected)
    await state.set_state(RegistrationStates.editing_interests)
    await callback.message.edit_text(
        "<b>Какими сферами вы интересуетесь?</b>\nВыберите один или несколько вариантов:",
        reply_markup=update_interests_keyboard(selected),
        parse_mode="HTML",
    )
    await callback.answer()


@registration_router.callback_query(
    RegistrationStates.editing_interests, F.data.startswith("interest_")
)
async def process_edit_interest_selection(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_interests", [])
    if callback.data in selected:
        selected.remove(callback.data)
    else:
        selected.append(callback.data)
    await state.update_data(selected_interests=selected)
    await callback.message.edit_reply_markup(
        reply_markup=update_interests_keyboard(selected)
    )
    await callback.answer()


@registration_router.callback_query(
    RegistrationStates.editing_interests, F.data == "interests_confirm"
)
async def confirm_edit_interests(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_interests", [])
    if not selected:
        await callback.answer("❌ Выберите хотя бы один интерес!", show_alert=True)
        return

    interest_names = get_interest_names()
    selected_names = [interest_names[i] for i in selected]
    interests_str = ", ".join(selected_names)

    async with async_session_maker() as session:
        repo = UserRepository(session)
        await repo.update(user_id=callback.from_user.id, interests=interests_str)

    await callback.message.edit_text(
        f"✅ Интересы обновлены: <b>{interests_str}</b>", parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.editing_menu)
    await callback.message.answer(
        "Что еще изменить?", reply_markup=get_edit_profile_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


@registration_router.callback_query(
    RegistrationStates.editing_menu, F.data == "edit_events"
)
async def edit_events(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    async with async_session_maker() as session:
        repo = UserRepository(session)
        user = await repo.get_by_id(user_id)

    selected = (
        _preselect_callbacks_from_names(user.events, get_event_names()) if user else []
    )

    await state.update_data(selected_events=selected)
    await state.set_state(RegistrationStates.editing_events)
    await callback.message.edit_text(
        "<b>Какие мероприятия Вам интересны?</b>\nВыберите один или несколько вариантов:",
        reply_markup=update_events_keyboard(selected),
        parse_mode="HTML",
    )
    await callback.answer()


@registration_router.callback_query(
    RegistrationStates.editing_events, F.data.startswith("event_")
)
async def process_edit_event_selection(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_events", [])
    if callback.data in selected:
        selected.remove(callback.data)
    else:
        selected.append(callback.data)
    await state.update_data(selected_events=selected)
    await callback.message.edit_reply_markup(
        reply_markup=update_events_keyboard(selected)
    )
    await callback.answer()


@registration_router.callback_query(
    RegistrationStates.editing_events, F.data == "events_confirm"
)
async def confirm_edit_events(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_events", [])
    if not selected:
        await callback.answer(
            "❌ Выберите хотя бы один тип мероприятий!", show_alert=True
        )
        return

    event_names = get_event_names()
    selected_names = [event_names[e] for e in selected]
    events_str = ", ".join(selected_names)

    async with async_session_maker() as session:
        repo = UserRepository(session)
        await repo.update(user_id=callback.from_user.id, events=events_str)

    await callback.message.edit_text(
        f"✅ Мероприятия обновлены: <b>{events_str}</b>", parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.editing_menu)
    await callback.message.answer(
        "Что еще изменить?", reply_markup=get_edit_profile_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


@registration_router.callback_query(
    RegistrationStates.editing_menu, F.data == "edit_about"
)
async def edit_about(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationStates.editing_about)
    await callback.message.edit_text(
        "<b>Расскажите о себе</b>\nМаксимум 150 слов.\nИли нажмите кнопку, чтобы пропустить.",
        reply_markup=get_skip_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@registration_router.message(RegistrationStates.editing_about)
async def process_edit_about(message: Message, state: FSMContext):
    try:
        about = validate_about(message.text)
        async with async_session_maker() as session:
            repo = UserRepository(session)
            await repo.update(user_id=message.from_user.id, about=about)

        about_text = about or "Не указано"
        await message.answer(
            f"✅ О себе обновлено: <b>{about_text}</b>", parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.editing_menu)
        await message.answer(
            "Что еще изменить?",
            reply_markup=get_edit_profile_keyboard(),
            parse_mode="HTML",
        )
    except ValidationError as e:
        await message.answer(str(e), parse_mode="HTML")

# Добавьте этот импорт в начало файла:
from utils.text_templates import get_text_template

# Замените функцию cmd_start на эту версию:


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
            # 🔴 ИСПРАВЛЕНО: Берем текст из БД
            welcome_text = await get_text_template(
                "welcome_return", first_name=user.first_name
            )
            await message.answer(welcome_text, parse_mode="HTML")
            await state.clear()
            return

    # 🔴 ИСПРАВЛЕНО: Берем текст приветствия из БД
    welcome_text = await get_text_template("welcome_new", first_name=first_name_tg)

    await message.answer(welcome_text, parse_mode="HTML")
    await state.set_state(RegistrationStates.waiting_for_name)

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import settings
from database import async_session_maker, UserRepository

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message):
    """Стандартный обработчик команды /start с сохранением пользователя"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name_tg = message.from_user.first_name

    # Сохраняем пользователя в БД
    async with async_session_maker() as session:
        repo = UserRepository(session)
        user, created = await repo.get_or_create(
            user_id=user_id, username=username, first_name_tg=first_name_tg
        )

    status = "новый пользователь" if created else "уже в базе"

    welcome_text = f"""
🚀 Привет, <b>{first_name_tg}</b>!

Я твой Telegram бот.
ID: <code>{user_id}</code>
Статус: {status}

Напиши что-нибудь, и я отвечу!
    """

    # Проверяем админа
    if settings.ADMIN_USER_ID and user_id == settings.ADMIN_USER_ID:
        welcome_text += "\n👑 Ты админ!"

    await message.answer(welcome_text, parse_mode="HTML")

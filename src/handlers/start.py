from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from src.config import settings

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message):
    """Стандартный обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or "без username"

    welcome_text = f"""
🚀 Привет, <b>{message.from_user.first_name}</b>!

Я твой Telegram бот.
ID: <code>{user_id}</code>

Напиши что-нибудь, и я отвечу!
    """

    # Проверяем админа
    if settings.ADMIN_USER_ID and user_id == settings.ADMIN_USER_ID:
        welcome_text += "\n👑 Ты админ!"

    await message.answer(welcome_text, parse_mode="HTML")

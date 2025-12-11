from aiogram import Router
from . import start  # Импорт start роутера

# Создаем главный роутер handlers
router = Router()

# Подключаем все роутеры модулей
router.include_router(start.start_router)

from aiogram import Router
from . import registration

# Создаем главный роутер handlers
router = Router()

# Подключаем все роутеры модулей
# Регистрация обрабатывает /start и дальнейшие шаги анкеты
router.include_router(registration.registration_router)

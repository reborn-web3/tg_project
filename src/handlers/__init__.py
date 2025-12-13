from aiogram import Router
from . import registration, admin

# Создаем главный роутер handlers
router = Router()

# Подключаем все роутеры модулей
# Регистрация обрабатывает /start и дальнейшие шаги анкеты
router.include_router(registration.registration_router)
# Админ-панель для редактирования текстов
router.include_router(admin.admin_router)

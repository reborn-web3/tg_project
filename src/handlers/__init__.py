from aiogram import Router
from . import registration, admin

# Создаем главный роутер handlers
router = Router()

# ВАЖНО: Подключаем ТОЛЬКО registration роутер!
# Старый start.py удалить или не подключать
router.include_router(registration.registration_router)
router.include_router(admin.admin_router)

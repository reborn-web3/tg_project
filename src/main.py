import json
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from handlers import router
from database import init_db
from database.init_texts import init_default_texts


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
# Хранилище для FSM (состояния)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)

db_ready = False


async def handler(event: dict, context):
    """Webhook handler для Yandex Cloud Functions"""
    global db_ready
    if not db_ready:
        await init_db()
        await init_default_texts()
        db_ready = True
        logger.info("Database initialized")

    try:
        body: str = event["body"]
        if not body or body.strip() == "{}":
            logger.warning("Empty webhook body received")
            return {"statusCode": 200, "body": ""}

        update_data = json.loads(body)
        if not update_data or "update_id" not in update_data:
            logger.warning(f"Invalid update data: {update_data}")
            return {"statusCode": 200, "body": ""}

        update = Update.model_validate(update_data)
        await dp.feed_update(bot, update)
        return {"statusCode": 200, "body": ""}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook body")
        return {"statusCode": 400, "body": "Invalid JSON"}
    except Exception as e:
        logger.error(f"Webhook handler error: {e}")
        return {"statusCode": 500, "body": ""}


async def main():
    """Локальный запуск бота для разработки"""
    logger.info("Initializing database...")
    await init_db()
    await init_default_texts()
    logger.info("Database initialized")

    logger.info("Initializing text templates...")
    await init_default_texts()
    logger.info("Text templates initialized")

    logger.info("Bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

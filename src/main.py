import json
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Update

from config import settings
from handlers import router
from database import init_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def handler(event: dict, context):
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
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")

    logger.info("Bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

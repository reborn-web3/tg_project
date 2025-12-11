import json
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Update

from config import settings
from handlers import router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


async def handler(event: dict, context):
    body: str = event["body"]
    update_data = json.loads(body) if body else {}

    await dp.feed_update(bot, Update.model_validate(update_data))

    return {"statusCode": 200, "body": ""}


async def main():
    dp.include_router(router)

    logger.info("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

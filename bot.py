# bot.py

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import router
from database import init_db


async def main():

    # Database Create
    init_db()

    # Bot Initialize
    bot = Bot(BOT_TOKEN)

    # Dispatcher
    dp = Dispatcher(
        storage=MemoryStorage()
    )

    # Include Router
    dp.include_router(router)

    print("✅ Bot Started Successfully!")

    # Remove old updates
    await bot.delete_webhook(
        drop_pending_updates=True
    )

    # Start Bot
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("❌ Bot Stopped")

import asyncio
from aiogram import Bot, Dispatcher
from handlers import start, callbacks, admin
from database import init_db
from config import BOT_TOKEN

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(callbacks.router)
    dp.include_router(admin.router)
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

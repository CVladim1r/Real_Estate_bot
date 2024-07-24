from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from handlers.common import router as common_router
from handlers.owners import router as owners_router
from handlers.comments import router as comments_router

bot = Bot(token='6848117166:AAGFRETuXNKKEABXp7opzvIzm5yDT6wN_GU')
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(common_router)
dp.include_router(owners_router)
dp.include_router(comments_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

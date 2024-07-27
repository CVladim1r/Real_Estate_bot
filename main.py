import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from handlers.common import router as common_router
from handlers.comments import router as comments_router
from handlers.owners import router as owners_router

async def main():
    bot = Bot(token="6848117166:AAGFRETuXNKKEABXp7opzvIzm5yDT6wN_GU")
    dp = Dispatcher()

    dp.include_router(common_router)
    dp.include_router(comments_router)
    dp.include_router(owners_router)

    await bot.set_my_commands([
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/info", description="Информация о боте")
    ])

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

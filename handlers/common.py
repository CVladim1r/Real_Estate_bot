from aiogram import types, Router
from aiogram.filters import Command
from aiogram import Bot
from keyboards.reply import main_menu, property_type_menu
from database.queries import get_active_properties

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message, bot: Bot):
    properties = get_active_properties()
    await bot.send_message(chat_id=message.chat.id, text="Выберите объект недвижимости:", reply_markup=main_menu(properties))

@router.message(lambda message: message.text in [prop[1] for prop in get_active_properties()])
async def choose_property(message: types.Message, bot: Bot):
    await bot.send_message(chat_id=message.chat.id, text="Выберите тип недвижимости:", reply_markup=property_type_menu())

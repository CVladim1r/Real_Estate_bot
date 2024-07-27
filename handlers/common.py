# handlers/common
from aiogram import Router, types
from aiogram.filters import Command

from keyboards.reply import get_houses_buttons
from keyboards.inline import get_properties_buttons, get_owners_buttons, get_comment_buttons
from database.queries import get_all_houses, get_properties_by_house_id, get_owners_by_property_id, get_comments_by_owner_id

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    houses = get_all_houses()
    await message.answer("Добро пожаловать! Выберите дом:", reply_markup=get_houses_buttons(houses))

@router.callback_query(lambda c: c.data.startswith('house_'))
async def process_house_callback(callback_query: types.CallbackQuery):
    house_id = int(callback_query.data.split('_')[1])
    properties = get_properties_by_house_id(house_id)
    await callback_query.message.edit_text("Выберите квартиру:", reply_markup=get_properties_buttons(properties))

@router.callback_query(lambda c: c.data.startswith('property_'))
async def process_property_callback(callback_query: types.CallbackQuery):
    property_id = int(callback_query.data.split('_')[1])
    owners = get_owners_by_property_id(property_id)
    await callback_query.message.edit_text("Выберите жильца:", reply_markup=get_owners_buttons(owners))

@router.callback_query(lambda c: c.data.startswith('owner_'))
async def process_owner_callback(callback_query: types.CallbackQuery):
    owner_id = int(callback_query.data.split('_')[1])
    comments = get_comments_by_owner_id(owner_id)
    await callback_query.message.edit_text("Выберите комментарий:", reply_markup=get_comment_buttons(comments))

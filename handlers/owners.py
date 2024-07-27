# handlers/owners
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.types import Message

from database.queries import get_all_properties
from keyboards.inline import get_properties_buttons

router = Router()

class PropertyState(StatesGroup):
    selecting_property = State()

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    properties = get_all_properties()
    await state.set_state(PropertyState.selecting_property)
    await message.answer("Выберите квартиру:", reply_markup=get_properties_buttons(properties))

@router.callback_query(lambda call: call.data.startswith("property"))
async def select_property(call: types.CallbackQuery, state: FSMContext):
    property_id = call.data.split("_")[1]
    await call.message.answer(f"Вы выбрали квартиру с ID: {property_id}")

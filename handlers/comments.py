# handlers/comments
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
import logging

from database.queries import insert_comment, get_comments_by_property_id, get_owners_by_property_id
from keyboards.inline import get_properties_buttons, get_owners_buttons, get_comment_buttons

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = Router()

class CommentState(StatesGroup):
    awaiting_comment = State()

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.set_state(CommentState.awaiting_comment)
    await state.update_data(property_id=None, owner_id=None, is_general=False)  # Обнуляем данные состояния
    await message.answer("Введите ваш комментарий:")

@router.message(StateFilter(CommentState.awaiting_comment))
async def add_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    owner_id = data.get("owner_id")
    property_id = data.get("property_id")
    is_general = data.get("is_general", False)

    logger.debug("Received comment from user. Owner ID: %s, Property ID: %s, Is General: %s", owner_id, property_id, is_general)
    
    if owner_id is None or property_id is None:
        await message.answer("Ошибка: идентификаторы владельца и объекта недвижимости не указаны.")
        await state.clear()
        return

    insert_comment(owner_id, property_id, message.text, is_general)
    await message.answer("Комментарий добавлен.", reply_markup=get_comment_buttons(property_id))
    await state.clear()


@router.callback_query(lambda call: call.data.startswith("owner_"))
async def select_owner(call: CallbackQuery, state: FSMContext):
    owner_id = int(call.data.split("_")[1])
    await state.update_data(owner_id=owner_id, is_general=False)
    await call.message.answer("Введите ваш комментарий для владельца:")

@router.callback_query(lambda call: call.data == "comment_general")
async def select_general_comment(call: CallbackQuery, state: FSMContext):
    await state.update_data(is_general=True)
    await call.message.answer("Введите ваш общий комментарий для объекта:")

@router.callback_query(lambda call: call.data.startswith("property_"))
async def select_property(call: CallbackQuery, state: FSMContext):
    property_id = int(call.data.split("_")[1])
    owners = get_owners_by_property_id(property_id)
    await state.update_data(property_id=property_id)
    await call.message.answer("Выберите собственника или оставьте общий комментарий:", reply_markup=get_owners_buttons(owners))

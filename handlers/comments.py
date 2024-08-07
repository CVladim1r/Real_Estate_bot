import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from database.queries import (get_properties_by_user_id, 
                              insert_general_comment, 
                              insert_comment, 
                              get_comments_by_property_id, 
                              get_properties_by_house_id,
                              save_properties_by_user_id)

from keyboards.inline import get_owners_buttons, get_comment_buttons, get_properties_buttons, get_back_button
from .common import PropertyState

router = Router()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PropertyStates(StatesGroup):
    awaiting_comment = State()

@router.callback_query(lambda call: call.data.startswith("owner_"))
async def select_owner(call: types.CallbackQuery, state: FSMContext):
    try:
        owner_id = int(call.data.split("_")[1])
        await state.update_data(owner_id=owner_id, is_general=False)
        await call.message.answer("Введите ваш комментарий для владельца:")
        await state.set_state(PropertyStates.awaiting_comment)
    except Exception as e:
        logger.error(f"Error in select_owner: {e}")
        await call.message.answer("Произошла ошибка. Попробуйте снова.")

@router.callback_query(lambda call: call.data == "comment_general")
async def select_general_comment(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.answer("Введите ваш общий комментарий для объекта:")
        await state.update_data(is_general=True)
        await state.set_state(PropertyStates.awaiting_comment)
    except Exception as e:
        logger.error(f"Error in select_general_comment: {e}")
        await call.message.answer("Произошла ошибка. Попробуйте снова.")

@router.message(StateFilter(PropertyStates.awaiting_comment))
async def add_comment(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        owner_id = data.get("owner_id")
        property_id = data.get("property_id")
        is_general = data.get("is_general", False)
        user_id = message.from_user.id

        logger.debug(f"Received comment: {message.text}")
        logger.debug(f"State data: {data}")

        if property_id is None:
            property_id = get_properties_by_user_id(user_id)
            await state.update_data(property_id=property_id)
            if not property_id:
                await message.answer("Ошибка: идентификатор объекта недвижимости не указан.")
                return

        if is_general:
            insert_general_comment(property_id, message.text)
            logger.info(f"Inserted general comment for property_id {property_id}")
        else:
            if owner_id is None:
                await message.answer("Ошибка: идентификатор владельца не указан.")
                return
            insert_comment(owner_id, property_id, message.text, is_general=False)
            logger.info(f"Inserted owner comment for owner_id {owner_id}, property_id {property_id}")

        await message.answer("Комментарий добавлен.")
        await message.answer("Что вы хотите сделать дальше?", reply_markup=get_back_button())
    except Exception as e:
        logger.error(f"Error in add_comment: {e}")
        await message.answer("Произошла ошибка при добавлении комментария. Попробуйте снова.")

@router.callback_query(lambda call: call.data == 'back_to_properties')
async def back_to_properties(call: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        house_id = data.get('house_id')
        if house_id is None:
            await call.message.answer("Ошибка: идентификатор дома не указан.")
            return

        properties = get_properties_by_house_id(house_id)
        if not properties:
            await call.message.answer("Нет квартир для отображения.")
        else:
            await call.message.edit_text("Выберите квартиру:", reply_markup=get_properties_buttons(properties))
    except Exception as e:
        logger.error(f"Error in back_to_properties: {e}")
        await call.message.answer("Произошла ошибка при возврате к списку квартир. Попробуйте снова.")

def register_comment_handlers(router: Router):
    router.callback_query.register(select_owner, lambda call: call.data.startswith("owner_"))
    router.callback_query.register(select_general_comment, lambda call: call.data == "comment_general")
    router.message.register(add_comment, StateFilter(PropertyStates.awaiting_comment))
    router.callback_query.register(back_to_properties, lambda call: call.data == 'back_to_properties')

register_comment_handlers(router)

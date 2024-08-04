from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from database.queries import insert_comment, get_comments_by_property_id, get_owners_by_property_id, get_properties_by_house_id
from keyboards.inline import get_owners_buttons, get_comment_buttons, get_properties_buttons, get_back_button

router = Router()

class CommentState(StatesGroup):
    awaiting_comment = State()

@router.callback_query(lambda call: call.data.startswith("owner_"))
async def select_owner(call: types.CallbackQuery, state: FSMContext):
    owner_id = int(call.data.split("_")[1])
    await state.update_data(owner_id=owner_id, is_general=False)
    await call.message.answer("Введите ваш комментарий для владельца:")
    await state.set_state(CommentState.awaiting_comment)

@router.callback_query(lambda call: call.data == "comment_general")
async def select_general_comment(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(is_general=True)
    await call.message.answer("Введите ваш общий комментарий для объекта:")
    await state.set_state(CommentState.awaiting_comment)

@router.message(StateFilter(CommentState.awaiting_comment))
async def add_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    owner_id = data.get("owner_id")
    property_id = data.get("property_id")
    is_general = data.get("is_general", False)

    if owner_id is None or property_id is None:
        await message.answer("Ошибка: идентификаторы владельца и объекта недвижимости не указаны.")
        await state.clear()
        return

    insert_comment(owner_id, property_id, message.text, is_general)
    await message.answer("Комментарий добавлен.")
    comments = get_comments_by_property_id(property_id)
    await message.answer("Комментарии к объекту:", reply_markup=get_comment_buttons(comments))

    await message.answer("Что вы хотите сделать дальше?", reply_markup=get_back_button())
    await state.clear()

@router.callback_query(lambda call: call.data == 'back_to_properties')
async def back_to_properties(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    house_id = data.get('house_id')
    if house_id is None:
        await call.message.answer("Ошибка: идентификатор дома не указан.")
        return
    properties = get_properties_by_house_id(house_id)
    await call.message.edit_text("Выберите квартиру:", reply_markup=get_properties_buttons(properties))

def register_comment_handlers(router: Router):
    router.callback_query.register(select_owner, lambda call: call.data.startswith("owner_"))
    router.callback_query.register(select_general_comment, lambda call: call.data == "comment_general")
    router.message.register(add_comment, StateFilter(CommentState.awaiting_comment))
    router.callback_query.register(back_to_properties, lambda call: call.data == 'back_to_properties')

import secrets
import datetime
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
import logging

from keyboards.inline import get_houses_buttons, get_properties_buttons, get_comment_buttons
from database.queries import get_all_houses, get_properties_by_house_id, get_property_by_number, insert_comment

router = Router()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PropertyState(StatesGroup):
    selecting_house = State()
    selecting_property = State()
    showing_property_info = State()
    awaiting_comment = State()

user_tokens = {}

def generate_token():
    return secrets.token_hex(16)

def register_user(user_id):
    token = generate_token()
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
    user_tokens[user_id] = {"token": token, "expires": expiration_date}
    return token

def is_token_valid(user_id, token):
    if user_id in user_tokens:
        stored_token_info = user_tokens[user_id]
        if stored_token_info["token"] == token and datetime.datetime.now() < stored_token_info["expires"]:
            return True
    return False

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    token = register_user(user_id)
    logger.info(f"Generated token for user {user_id}: {token}")
    
    await message.answer(f"Ваш токен для доступа: {token}\nСрок действия: 30 дней.")
    await message.answer("Введите ваш токен для продолжения:")

@router.message(lambda message: True)  # Handling any text message
async def token_command(message: types.Message, state: FSMContext):
    token = message.text
    user_id = message.from_user.id
    await state.update_data(token=token)
    houses = get_all_houses()
    logger.debug(f"Fetched houses: {houses}")
    await state.clear()
    await state.set_state(PropertyState.selecting_house)
    await message.answer("Выберите дом или введите адрес:", reply_markup=get_houses_buttons(houses))

@router.callback_query(lambda call: call.data.startswith("house_"))
async def process_house_selection(callback_query: types.CallbackQuery, state: FSMContext):
    house_id = int(callback_query.data.split("_")[1])
    properties = get_properties_by_house_id(house_id)
    logger.debug(f"Selected house ID: {house_id}, fetched properties: {properties}")
    await state.update_data(house_id=house_id, properties=properties, current_page=0)
    await state.set_state(PropertyState.selecting_property)
    await callback_query.message.edit_text("Выберите квартиру или введите номер:", reply_markup=get_properties_buttons(properties, current_page=0))

@router.message(PropertyState.selecting_house)
async def process_house_address(message: types.Message, state: FSMContext):
    address = message.text
    houses = get_all_houses()
    selected_house = next((house for house in houses if house['address'] == address), None)

    if selected_house:
        house_id = selected_house['id']
        properties = get_properties_by_house_id(house_id)
        await state.update_data(house_id=house_id, properties=properties, current_page=0)
        await state.set_state(PropertyState.selecting_property)
        await message.answer("Выберите квартиру или введите номер:", reply_markup=get_properties_buttons(properties, current_page=0))
    else:
        await message.answer("Дом не найден. Попробуйте снова.")

@router.message(PropertyState.selecting_property)
async def process_property_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    token = data.get("token")
    
    property_number = message.text
    property_info = get_property_by_number(property_number)
    logger.debug(f"Entered property number: {property_number}, fetched property info: {property_info}")
    
    if not property_info:
        await message.answer("Квартира не найдена. Попробуйте снова.")
        return
    
    response_text = (
        f"Номер помещения: {property_info['number']}\n"
        f"Площадь: {property_info['area']} кв.м.\n"
        f"ФИО собственников: {', '.join([owner['name'] for owner in property_info['owners']])}\n"
        f"Дата рождения: {', '.join([owner['dob'] for owner in property_info['owners']])}\n"
        f"Назначение помещения: {property_info['purpose']}\n"
        f"Доля: {', '.join([owner['share'] for owner in property_info['owners']])}\n"
        f"Комментарий: {property_info['comment']}\n"
    )
    logger.debug(f"Generated response text for property info: {response_text}")
    await message.answer(response_text)

    await state.update_data(property_info=property_info)
    await state.set_state(PropertyState.showing_property_info)
    await message.answer("Выберите действие:", reply_markup=get_comment_buttons(property_info))

@router.callback_query(lambda call: call.data.startswith("comment_owner_") or call.data == "comment_general")
async def process_comment_selection(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback_query.from_user.id
    token = data.get("token")

    await state.update_data(comment_target=callback_query.data)
    await state.set_state(PropertyState.awaiting_comment)
    await callback_query.message.answer("Введите ваш комментарий:")

@router.message(PropertyState.awaiting_comment)
async def process_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    token = data.get("token")

    property_info = data.get("property_info")
    comment_target = data.get("comment_target")
    house_id = data.get("house_id")

    owner_index = None
    if comment_target.startswith("comment_owner_"):
        owner_index = int(comment_target.split("_")[-1]) - 1

    logger.debug(f"Inserting comment for property: {property_info['number']}, comment: {message.text}, owner index: {owner_index}")
    insert_comment(property_info["number"], message.text, owner_index)

    await message.answer("Комментарий добавлен.")

    # Определите состояние для возврата
    if owner_index is not None:
        return_to_property = True
    else:
        return_to_property = False

    if return_to_property:
        # Возвращаемся к информации о квартире
        response_text = (
            f"Номер помещения: {property_info['number']}\n"
            f"Площадь: {property_info['area']} кв.м.\n"
            f"ФИО собственников: {', '.join([owner['name'] for owner in property_info['owners']])}\n"
            f"Дата рождения: {', '.join([owner['dob'] for owner in property_info['owners']])}\n"
            f"Назначение помещения: {property_info['purpose']}\n"
            f"Доля: {', '.join([owner['share'] for owner in property_info['owners']])}\n"
            f"Комментарий: {property_info['comment']}\n"
        )
        await message.answer(response_text)
        await state.set_state(PropertyState.showing_property_info)
        await message.answer("Выберите действие:", reply_markup=get_comment_buttons(property_info))
    else:
        # Возвращаемся к списку квартир в доме
        properties = get_properties_by_house_id(house_id)
        await state.set_state(PropertyState.selecting_property)
        await message.answer("Выберите квартиру или введите номер:", reply_markup=get_properties_buttons(properties))

@router.callback_query(lambda call: call.data == 'back_to_houses')
async def back_to_houses(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback_query.from_user.id
    token = data.get("token")
    
    houses = get_all_houses()
    logger.debug(f"Returning to house selection, fetched houses: {houses}")
    await state.clear()
    await state.set_state(PropertyState.selecting_house)
    await callback_query.message.edit_text("Выберите дом или введите адрес:", reply_markup=get_houses_buttons(houses))

@router.callback_query(lambda call: call.data == 'back_to_properties')
async def back_to_properties(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback_query.from_user.id
    token = data.get("token")

    house_id = data.get("house_id")
    properties = get_properties_by_house_id(house_id)
    logger.debug(f"Returning to property selection for house ID: {house_id}, fetched properties: {properties}")
    await state.set_state(PropertyState.selecting_property)
    await callback_query.message.edit_text("Выберите квартиру или введите номер:", reply_markup=get_properties_buttons(properties))

@router.callback_query(lambda call: call.data.startswith("page_"))
async def paginate_houses(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        current_page = int(callback_query.data.split("_")[1])
        houses = get_all_houses()
        logger.debug(f"Paginating houses, current page: {current_page}, houses range: {houses[current_page * 5 : (current_page + 1) * 5]}")
        await callback_query.message.edit_reply_markup(reply_markup=get_houses_buttons(houses, current_page))
    except Exception as e:
        logger.error(f"Error paginating houses: {e}")

@router.callback_query(lambda call: call.data.startswith("properties_next_") or call.data.startswith("properties_prev_"))
async def paginate_properties(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        current_page = data.get("current_page", 0)
        house_id = data.get("house_id")
        properties = get_properties_by_house_id(house_id)
        
        if callback_query.data.startswith("properties_next_"):
            current_page += 1
        elif callback_query.data.startswith("properties_prev_"):
            current_page -= 1

        logger.debug(f"Paginating properties, current page: {current_page}, properties range: {properties[current_page * 5 : (current_page + 1) * 5]}")
        await state.update_data(current_page=current_page)
        await callback_query.message.edit_reply_markup(reply_markup=get_properties_buttons(properties, current_page))
    except Exception as e:
        logger.error(f"Error paginating properties: {e}")

def register_common_handlers(router: Router):
    router.message.register(start_command, Command("start"))
    router.message.register(token_command, StateFilter(PropertyState.selecting_house))
    router.callback_query.register(process_house_selection, lambda call: call.data.startswith("house_"))
    router.message.register(process_house_address, PropertyState.selecting_house)
    router.message.register(process_property_number, PropertyState.selecting_property)
    router.callback_query.register(process_comment_selection, lambda call: call.data.startswith("comment_owner_") or call.data == "comment_general")
    router.message.register(process_comment, PropertyState.awaiting_comment)
    router.callback_query.register(back_to_houses, lambda call: call.data == 'back_to_houses')
    router.callback_query.register(back_to_properties, lambda call: call.data == 'back_to_properties')
    router.callback_query.register(paginate_houses, lambda call: call.data.startswith("page_"))
    router.callback_query.register(paginate_properties, lambda call: call.data.startswith("properties_next_") or call.data.startswith("properties_prev_"))
    router.include_router(router)

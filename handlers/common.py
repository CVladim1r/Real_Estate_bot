import secrets
import datetime
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
import logging
import json
from .file import *
from keyboards.inline import get_back_button, get_houses_buttons, get_properties_buttons, get_comment_buttons, get_owners_buttons
from database.queries import update_user_state, get_user_last_house, load_active_property_id_db, save_active_property_id_db, get_owners_by_property_id, get_property_id_by_number_and_house, get_user_token, get_all_houses, get_properties_by_house_id, get_property_by_number, insert_comment, add_user_token

router = Router()

class PropertyState(StatesGroup):
    selecting_house = State()
    selecting_property = State()
    showing_property_info = State()
    awaiting_comment = State()
    awaiting_token = State()
    active_property_id = State()

user_tokens = {}

def generate_token():
    return secrets.token_hex(8)

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
    token = get_user_token(user_id)
    if token is None:
        token = register_user(user_id)
        add_user_token(user_id, token)
    logger.info(f"Generated token for user {user_id}: {token}")
    
    await state.update_data(token=token)
    await state.set_state(PropertyState.awaiting_token)
    await message.answer(f"Ваш токен для доступа: {token}\nСрок действия: 30 дней.")
    await message.answer("Введите ваш токен для продолжения:")

@router.message(PropertyState.awaiting_token)
async def token_command(message: types.Message, state: FSMContext):
    token = message.text
    user_id = message.from_user.id
    data = await state.get_data() 
    stored_token = data.get('token')

    if token == stored_token:
        houses = get_all_houses()
        logger.debug(f"Fetched houses: {houses}")
        await state.set_state(PropertyState.selecting_house)
        await message.answer("Выберите дом или введите адрес:", reply_markup=get_houses_buttons(houses))
    else:
        await message.answer("Токен недействителен или истек. Пожалуйста, запросите новый токен с помощью команды /start.")

@router.callback_query(lambda call: call.data.startswith("house_"))
async def process_house_selection(callback_query: types.CallbackQuery, state: FSMContext):
    house_id = int(callback_query.data.split("_")[1])
    properties = get_properties_by_house_id(house_id)
    user_id = callback_query.message.from_user.id
    update_user_state(user_id, house_id)
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
    property_number = message.text
    data = await state.get_data()
    house_id = data.get('house_id')

    property_id = get_property_id_by_number_and_house(property_number, house_id)
    if property_id is None:
        await message.answer("Квартира не найдена. Попробуйте снова.")
        return

    property_info = get_property_by_number(property_id)
    logger.debug(f"Fetched property info: {property_info}")

    user_id = message.from_user.id
    save_active_property_id_db(user_id, property_id)

    await state.update_data(property_number=property_number, property_info=property_info, active_property_id=property_id)
    save_active_property_id(user_id, property_id)
    logger.debug(f"State updated with active_property_id: {property_id}")

    owners = get_owners_by_property_id(property_id)
    logger.debug(f"Fetched owners: {owners}")
    if not owners:
        await message.answer("Собственники не найдены. Попробуйте снова.")
        return

    response_text = (
        f"**Номер помещения:** {property_info['number']}\n"
        f"**Площадь:** {property_info['area']} кв.м.\n"
        f"**Тип помещения:** {property_info['type']}\n"
        f"**Форма собственности:** {property_info['ownership_form']}\n"
        f"**Кадастровый номер:** {property_info.get('cadastral_number', 'Не указан')}\n"
        f"**Документ о праве собственности:** {property_info.get('ownership_doc', 'Не указан')}\n"
        f"**Общий комментарий:** {property_info.get('general_comment', 'Не указан')}\n"
        f"**Собственники:**\n"
        + '\n'.join(
            f" - {owner[2]}, дата рождения: {owner[3].strftime('%d.%m.%Y') if owner[3] else 'Не указана'}, доля: {owner[4]}м/кв2"
            for owner in owners
        )
    )
    await state.update_data(property_number=property_number, property_info=property_info, active_property_id=property_id)

    await message.answer(response_text, parse_mode='Markdown')
    await state.set_state(PropertyState.showing_property_info)
    await message.answer("Выберите действие:", reply_markup=get_comment_buttons(property_info))

@router.callback_query(lambda call: call.data == "back")
async def go_back(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.message.from_user.id

    saved_user_id, property_id = load_active_property_id_db(user_id)
    
    if saved_user_id != user_id or property_id is None:
        await callback_query.message.answer("Активная квартира не найдена. Выберите квартиру заново.")
        await state.set_state(PropertyState.selecting_property)
        return

    property_info = get_property_by_number(property_id)

    owners = get_owners_by_property_id(property_id)


    response_text = (
        f"**Номер помещения:** {property_info['number']}\n"
        f"**Площадь:** {property_info['area']} кв.м.\n"
        f"**Тип помещения:** {property_info['type']}\n"
        f"**Форма собственности:** {property_info['ownership_form']}\n"
        f"**Кадастровый номер:** {property_info.get('cadastral_number', 'Не указан')}\n"
        f"**Документ о праве собственности:** {property_info.get('ownership_doc', 'Не указан')}\n"
        f"**Общий комментарий:** {property_info.get('general_comment', 'Не указан')}\n"
        f"**Собственники:**\n"
        + '\n'.join(
            f" - {owner[2]}, дата рождения: {owner[3].strftime('%d.%m.%Y')}, доля: {owner[4]}м/кв2"
            for owner in owners
        )
    )

    await callback_query.message.answer(response_text, parse_mode='Markdown')
    await state.set_state(PropertyState.showing_property_info)
    await callback_query.message.answer("Выберите действие:", reply_markup=get_comment_buttons(property_info))

@router.callback_query(lambda call: call.data.startswith("comment_owner_") or call.data == "comment_general")
async def process_comment_selection(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(comment_target=callback_query.data)
    await state.set_state(PropertyState.awaiting_comment)
    await callback_query.message.answer("Введите ваш комментарий:")

@router.message(PropertyState.awaiting_comment)
async def process_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    property_info = data.get("property_info")
    comment_target = data.get("comment_target")
    house_id = data.get("house_id")
    active_property_id = data.get("active_property_id")

    logger.debug(f"Processing comment. Property info: {property_info}, Comment target: {comment_target}, Active property ID: {active_property_id}")

    if not property_info:
        await message.answer("Комментарий отправлен!", reply_markup=get_back_button())
        return

    owner_index = None
    if comment_target and comment_target.startswith("comment_owner_"):
        try:
            owner_index = int(comment_target.split("_")[-1]) - 1
        except ValueError:
            await message.answer("Комментарий отправлен!", reply_markup=get_back_button())
            return

    logger.debug(f"Inserting comment for property: {property_info['number']}, comment: {message.text}, owner index: {owner_index}")
    insert_comment(property_info["number"], message.text, owner_index)

    await message.answer("Комментарий добавлен.")

    if owner_index is not None:
        owners = get_owners_by_property_id(active_property_id)
        if not owners:
            await message.answer("Собственники не найдены.")
            return

        response_text = (
            f"📦 **Номер помещения:** {property_info['number']}\n"
            f"📏 **Площадь:** {property_info['area']} кв.м.\n"
            f"🏢 **Тип помещения:** {property_info['type']}\n"
            f"📝 **Форма собственности:** {property_info['ownership_form']}\n"
            f"🔢 **Кадастровый номер:** {property_info.get('cadastral_number', 'Не указан')}\n"
            f"📄 **Документ о праве собственности:** {property_info.get('ownership_doc', 'Не указан')}\n"
            f"🗒️ **Общий комментарий:** {property_info.get('general_comment', 'Не указан')}\n\n"
            f"👤 **Собственник {owner_index + 1}:**\n"
            f" - {owners[owner_index]['fio']}, дата рождения: {owners[owner_index]['birth_date'].strftime('%d.%m.%Y')}, доля: {owners[owner_index]['share']}м/кв2\n\n"
            f"📌 **Комментарий:** {message.text}"
        )
    else:
        response_text = (
            f"📦 **Номер помещения:** {property_info['number']}\n"
            f"📏 **Площадь:** {property_info['area']} кв.м.\n"
            f"🏢 **Тип помещения:** {property_info['type']}\n"
            f"📝 **Форма собственности:** {property_info['ownership_form']}\n"
            f"🔢 **Кадастровый номер:** {property_info.get('cadastral_number', 'Не указан')}\n"
            f"📄 **Документ о праве собственности:** {property_info.get('ownership_doc', 'Не указан')}\n"
            f"🗒️ **Общий комментарий:** {property_info.get('general_comment', 'Не указан')}\n"
            f"🗒️ **Комментарий:** {message.text}"
        )

    await message.answer(response_text, parse_mode='Markdown')
    await state.set_state(PropertyState.showing_property_info)
    await message.answer("Выберите действие:", reply_markup=get_comment_buttons(property_info))


@router.callback_query(lambda call: call.data == 'back_to_houses')
async def back_to_houses(callback_query: types.CallbackQuery, state: FSMContext):
    houses = get_all_houses()
    logger.debug(f"Returning to house selection, fetched houses: {houses}")
    await state.clear()
    await state.set_state(PropertyState.selecting_house)
    await callback_query.message.edit_text("Выберите дом или введите адрес:", reply_markup=get_houses_buttons(houses))

@router.callback_query(lambda call: call.data == 'back_to_properties')
async def back_to_properties(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback_query.message.from_user.id
    house_id = get_user_last_house(user_id)
    if not house_id:
        house_id = get_user_last_house(user_id)
    
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
        user_id = callback_query.message.from_user.id
        current_page = data.get("current_page", 0)
        house_id = data.get("house_id")

        if not house_id:
            house_id = get_user_last_house(user_id)
            await state.update_data(house_id=house_id)

        properties = get_properties_by_house_id(house_id)
        
        if properties is None:
            properties = []

        if callback_query.data.startswith("properties_next_"):
            current_page += 1
        elif callback_query.data.startswith("properties_prev_"):
            current_page -= 1

        num_properties = len(properties)
        total_pages = (num_properties + 47) // 48  
        
        if current_page < 0:
            current_page = 0
        elif current_page >= total_pages:
            current_page = total_pages - 1

        await state.update_data(current_page=current_page)

        start_index = current_page * 48
        end_index = (current_page + 1) * 48
        properties_page = properties[start_index:end_index]


        await callback_query.message.edit_reply_markup(reply_markup=get_properties_buttons(properties, current_page))

    except Exception as e:
        logger.error(f"Error paginating properties: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке запроса.")


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
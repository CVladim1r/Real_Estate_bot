from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database.queries import get_general_comment_by_property_id, save_active_property_id_db, get_all_properties, get_owners_by_property_id, get_property_by_number, save_active_owner_id_db, load_active_owner_id_db
from keyboards.inline import get_properties_buttons, get_owners_buttons

from .common import PropertyState

router = Router()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    if text is None:
        return ""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    properties = get_all_properties()
    logger.debug(f"Fetched properties: {properties}")
    if not properties:
        await message.answer("Не удалось загрузить список квартир. Попробуйте позже.")
        return
    await state.set_state(PropertyState.selecting_property)
    await message.answer("Выберите квартиру:", reply_markup=get_properties_buttons(properties))

@router.callback_query(lambda call: call.data.startswith("property_"))
async def select_property(call: types.CallbackQuery, state: FSMContext):
    try:
        property_id = int(call.data.split("_")[1])
        logger.debug(f"Selected property ID: {property_id}")
        save_active_property_id_db(call.message.from_user.id, property_id)
        general_comment = get_general_comment_by_property_id(property_id)
        property_info = get_property_by_number(property_id)
        logger.debug(f"Fetched property info: {property_info}")
        owners = get_owners_by_property_id(property_id)
    
        if not property_info:
            await call.message.answer("Квартира не найдена. Попробуйте снова.")
            return

        response_text = (
            f"**Номер помещения:** {escape_markdown(str(property_info['number']))}\n"
            f"**Площадь:** {property_info['area']} кв.м.\n"
            f"**Тип помещения:** {escape_markdown(property_info['type'])}\n"
            f"**Собственники:**\n"
            + '\n'.join(
                f" - {escape_markdown(owner['fio'])}, дата рождения: {owner['birth_date'] if isinstance(owner['birth_date'], str) else owner['birth_date'].strftime('%d.%m.%Y')}, доля: {owner['share']}м/кв2, комментарий: {escape_markdown(owner['comment'])}"
                for owner in property_info['owners'] 
            )
            + '\n\n'
            + f"**Общий комментарий:** {escape_markdown(general_comment)}\n"
        )

        logger.debug(f"Generated response text for property info: {response_text}")
        await call.message.answer(response_text, parse_mode='Markdown')

        owners = get_owners_by_property_id(property_id)
        logger.debug(f"Fetched owners: {owners}")
        if not owners:
            await call.message.answer("Собственники не найдены. Попробуйте снова.")
            return

        await state.update_data(property_id=property_id)
        await call.message.answer("Выберите собственника или оставьте общий комментарий:", reply_markup=get_owners_buttons(owners))
        await state.set_state(PropertyState.selecting_owner)
    except Exception as e:
        logger.error(f"Error processing property selection: {e}")
        await call.message.answer("Произошла ошибка при обработке выбора квартиры. Попробуйте снова.")

def register_owner_handlers(router: Router):
    router.callback_query.register(select_property, lambda call: call.data.startswith("property_"))

register_owner_handlers(router)

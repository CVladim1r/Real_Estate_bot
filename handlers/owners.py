from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database.queries import get_all_properties, get_owners_by_property_id, get_property_by_number
from keyboards.inline import get_properties_buttons, get_owners_buttons

router = Router()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PropertyState(StatesGroup):
    selecting_property = State()
    showing_property_info = State()
    selecting_owner = State()

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
        
        # Fetch property info from the database
        property_info = get_property_by_number(property_id)
        logger.debug(f"Fetched property info: {property_info}")

        if not property_info:
            await call.message.answer("Квартира не найдена. Попробуйте снова.")
            return

        # Generate response text
        response_text = (
            f"Номер помещения: {property_info['id']}\n"
            f"Площадь: {property_info['area']} кв.м.\n"
            f"ФИО собственников: {', '.join([owner['fio'] for owner in property_info['owners']])}\n"
            f"Дата рождения: {', '.join([owner['birth_date'].strftime('%d.%m.%Y') if owner['birth_date'] else 'неизвестно' for owner in property_info['owners']])}\n"
            f"Назначение помещения: {property_info['type']}\n"
            f"Доля: {', '.join([str(owner['share']) for owner in property_info['owners']])}\n"
            f"Комментарий: {property_info['general_comment'] or 'нет комментария'}\n"
        )
        logger.debug(f"Generated response text for property info: {response_text}")
        await call.message.answer(response_text)

        # Fetch owners from the database
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
    router.message.register(start_command, Command("start"))
    router.callback_query.register(select_property, lambda call: call.data.startswith("property_"))

register_owner_handlers(router)

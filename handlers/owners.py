from aiogram import types, Router
from aiogram import Bot
from database.queries import get_property_info
from keyboards.reply import comment_menu

router = Router()

@router.message(lambda message: message.text.isdigit())
async def enter_property_number(message: types.Message, bot: Bot):
    property_id = message.text
    property_info = get_property_info(property_id)
    if not property_info:
        await bot.send_message(chat_id=message.chat.id, text="Информация о данном помещении не найдена.")
        return
    info = f"""
    Номер помещения: {property_info[0][0]}
    Площадь: {property_info[0][1]} кв.м.
    ФИО собственников: {', '.join([owner[2] for owner in property_info])}
    Дата рождения: {', '.join([owner[3].strftime('%d.%m.%Y') for owner in property_info])}
    Назначение помещения: {property_info[0][4]}
    Доля: {property_info[0][5]}%
    Комментарий: {property_info[0][6] if property_info[0][6] else "Нет комментариев"}
    """
    await bot.send_message(chat_id=message.chat.id, text=info, reply_markup=comment_menu(property_info))

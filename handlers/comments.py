from aiogram import types, Router
from aiogram import Bot
from database.queries import add_comment

router = Router()

@router.message(lambda message: message.text.startswith("Оставить комментарий "))
async def add_comment_handler(message: types.Message, bot: Bot):
    parts = message.text.split(' ', 3)
    if len(parts) < 4:
        await bot.send_message(chat_id=message.chat.id, text="Неверный формат комментария. Используйте: <property_id> <owner_id> <Комментарий>")
        return
    property_id, owner_id, comment = parts[1], parts[2], parts[3]
    add_comment(property_id, owner_id, comment)
    await bot.send_message(chat_id=message.chat.id, text="Комментарий успешно добавлен.")

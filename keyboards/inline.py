from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_houses_buttons(houses):
    builder = InlineKeyboardBuilder()
    logger.debug("Creating house buttons with houses: %s", houses)
    for house in houses:
        text = f"Дом: {house[1]}"  # Предполагаем, что house[1] это адрес дома
        logger.debug("Adding button with text: %s", text)
        builder.add(InlineKeyboardButton(text=text, callback_data=f"house_{house[0]}"))
    keyboard = builder.as_markup()
    logger.info("House buttons created successfully.")
    return keyboard

def get_properties_buttons(properties):
    builder = InlineKeyboardBuilder()
    logger.debug("Creating property buttons with properties: %s", properties)
    for prop in properties:
        # Формируем текст кнопки, предполагая, что prop[2] это номер квартиры, prop[3] площадь, prop[4] дополнительная информация
        text = f"Квартира {prop[2]} - {prop[3]} м², {prop[4]}"
        logger.debug("Adding button with text: %s", text)
        # Добавляем кнопку
        builder.add(InlineKeyboardButton(text=text, callback_data=f"property_{prop[0]}"))
    keyboard = builder.as_markup()
    logger.info("Property buttons created successfully.")
    return keyboard

def get_owners_buttons(owners):
    builder = InlineKeyboardBuilder()
    logger.debug("Creating owner buttons with owners: %s", owners)
    for owner in owners:
        text = f"ФИО: {owner[2]}, Доля: {owner[4]}"  # Предполагаем, что owner[2] это ФИО жильца и owner[4] это доля
        logger.debug("Adding button with text: %s", text)
        builder.add(InlineKeyboardButton(text=text, callback_data=f"owner_{owner[0]}"))
    keyboard = builder.as_markup()
    logger.info("Owner buttons created successfully.")
    return keyboard

def get_comment_buttons(comments):
    builder = InlineKeyboardBuilder()
    logger.debug("Creating comment buttons with comments: %s", comments)
    for comment in comments:
        if len(comment) > 0:  # Проверяем, что comment содержит элементы
            text = f"Комментарий ID {comment[0]}: {comment[1]}"  # Преобразуем значение в строку и добавляем текст комментария
            logger.debug("Adding button for comment ID: %s", text)
            builder.add(InlineKeyboardButton(text=text, callback_data=f"comment_{comment[0]}"))  # Используем callback_data
        else:
            logger.warning("Comment list is empty or does not contain expected elements: %s", comment)
    keyboard = builder.as_markup()
    logger.info("Comment buttons created successfully.")
    return keyboard

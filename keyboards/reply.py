from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_houses_buttons(houses):
    builder = InlineKeyboardBuilder()
    logger.debug("Creating houses buttons with houses: %s", houses)
    for house in houses:
        text = house[1]
        callback_data = f"house_{house[0]}"
        logger.debug("Adding button with text: %s", text)
        builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    keyboard = builder.as_markup()
    logger.info("Houses buttons created successfully.")
    return keyboard

def get_comment_buttons(comments):
    builder = InlineKeyboardBuilder()
    logger.debug("Creating comment buttons with comments: %s", comments)
    for comment in comments:
        if len(comment) > 0:
            text = str(comment[0])
            logger.debug("Adding button for comment ID: %s", text)
            builder.add(InlineKeyboardButton(text=f"Комментарий {text}", callback_data=f"comment_{text}"))
        else:
            logger.warning("Comment list is empty or does not contain expected elements: %s", comment)
    logger.info("Comment buttons created successfully.")
    keyboard = builder.as_markup()
    return keyboard

def get_main_menu(properties):
    builder = InlineKeyboardBuilder()
    logger.debug("Creating main menu with properties: %s", properties)
    for prop in properties:
        text = str(prop[1])
        logger.debug("Adding button with text: %s", text)
        builder.add(InlineKeyboardButton(text=text, callback_data=text))
    keyboard = builder.as_markup()
    logger.info("Main menu created successfully.")
    return keyboard

def get_owner_buttons(owners):
    builder = InlineKeyboardBuilder()
    logger.debug("Creating owner buttons with owners: %s", owners)
    for owner in owners:
        if len(owner) > 2 and isinstance(owner[2], str):
            text = f"Оставить комментарий {owner[2]}"
            logger.debug("Adding button for owner: %s", owner[2])
            builder.add(InlineKeyboardButton(text=text, callback_data=f"comment_{owner[2]}"))
        else:
            logger.warning("Expected owner with at least 3 elements and a string in position 2 but got: %s", owner)
    builder.add(InlineKeyboardButton(text="Оставить комментарий общий", callback_data="comment_general"))
    logger.info("Owner buttons created successfully.")
    keyboard = builder.as_markup()
    return keyboard

def get_comment_buttons(comments):
    builder = InlineKeyboardBuilder()
    logger.debug("Creating comment buttons with comments: %s", comments)
    for comment in comments:
        if len(comment) > 0:
            text = str(comment[0])
            logger.debug("Adding button for comment ID: %s", text)
            builder.add(InlineKeyboardButton(text=f"Комментарий {text}", callback_data=f"comment_{text}"))
        else:
            logger.warning("Comment list is empty or does not contain expected elements: %s", comment)
    logger.info("Comment buttons created successfully.")
    keyboard = builder.as_markup()
    return keyboard

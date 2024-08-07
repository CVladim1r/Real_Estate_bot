from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PROPERTIES_PER_PAGE = 50

def get_houses_buttons(houses, current_page=0):
    buttons = []
    for house in houses[current_page*5:(current_page+1)*5]:
        buttons.append([InlineKeyboardButton(text=house[1], callback_data=f"house_{house[0]}")])

    pagination_buttons = []
    if current_page > 0:
        pagination_buttons.append(InlineKeyboardButton(text="Назад", callback_data=f"page_{current_page-1}"))
    if (current_page + 1) * 5 < len(houses):
        pagination_buttons.append(InlineKeyboardButton(text="Вперед", callback_data=f"page_{current_page+1}"))

    if pagination_buttons:
        buttons.append(pagination_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_comment_buttons(property_info):
    buttons = [
        [InlineKeyboardButton(text="Добавить комментарий", callback_data="comment_general")],
    ]
    for i, owner in enumerate(property_info['owners'], start=1):
        buttons.append([InlineKeyboardButton(text=f"Комментарий владельцу {i}", callback_data=f"comment_owner_{i}")])

    buttons.append([InlineKeyboardButton(text="Назад к квартирам", callback_data="back_to_properties")])
    buttons.append([InlineKeyboardButton(text="Назад к домам", callback_data="back_to_houses")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_properties_buttons(properties, current_page=0):
    builder = InlineKeyboardBuilder()
    
    for prop in properties[current_page*48:(current_page+1)*48]:
        text = f"Кв. {prop[2]}"
        builder.add(InlineKeyboardButton(text=text, callback_data=f"property_{prop[0]}"))
    
    builder.adjust(4)
    
    if current_page > 0:
        builder.add(InlineKeyboardButton(text="Назад", callback_data=f"properties_prev_{current_page-1}"))
    if (current_page + 1) * 48 < len(properties):
        builder.add(InlineKeyboardButton(text="Вперед", callback_data=f"properties_next_{current_page+1}"))
    
    builder.adjust(4)
    
    return builder.as_markup()

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_owners_buttons(owners):
    builder = InlineKeyboardBuilder()

    for owner in owners:
        try:
            owner_id = owner[0]
            fio = owner[2]  
            share = owner[4] 
            text = f"{fio}"
            callback_data = f"owner_{owner_id}"
            

            builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        except IndexError as e:
            print(f"IndexError: {e} - owner data: {owner}")
        except Exception as e:
            print(f"Exception: {e} - owner data: {owner}")

    builder.add(InlineKeyboardButton(text="Оставить общий комментарий", callback_data="comment_general"))
    builder.add(InlineKeyboardButton(text="Вернуться к выбору квартиры", callback_data="back_to_properties"))
    builder.add(InlineKeyboardButton(text="Вернуться к выбору адреса", callback_data="back_to_houses"))

    builder.adjust(1)

    return builder.as_markup()


def get_back_button():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Вернуться к выбору адреса", callback_data="back_to_houses"))
    builder.add(InlineKeyboardButton(text="Вернуться к выбору квартиры", callback_data="back_to_properties"))
    builder.add(InlineKeyboardButton(text="Вернуться к активной квартире", callback_data="back"))
    builder.adjust(1)
    return builder.as_markup()

def get_comment_buttons(property_info):
    builder = InlineKeyboardBuilder()
    
    for owner in property_info['owners']:
        fio = owner['fio']
        owner_id = owner.get('id', None)
        text = f"{fio}"
        callback_data = f"comment_owner_{owner_id}" if owner_id is not None else f"comment_owner_unknown"
        builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    
    builder.add(InlineKeyboardButton(text="Оставить комментарий общий", callback_data="comment_general"))
    builder.add(InlineKeyboardButton(text="Вернуться к выбору адреса", callback_data="back_to_houses"))
    builder.add(InlineKeyboardButton(text="Вернуться к выбору квартиры", callback_data="back_to_properties"))

    builder.adjust(1)

    return builder.as_markup()
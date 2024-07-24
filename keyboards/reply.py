from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu(properties):
    buttons = [KeyboardButton(text=prop[1]) for prop in properties]
    return ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)

def property_type_menu():
    buttons = [
        KeyboardButton(text="Жилое"),
        KeyboardButton(text="Нежилое")
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)

def comment_menu(owners):
    buttons = [KeyboardButton(text=f"Оставить комментарий {owner[2]}") for owner in owners]
    buttons.append(KeyboardButton(text="Оставить общий комментарий"))
    return ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)

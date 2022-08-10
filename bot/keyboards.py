from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def schedule_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = list()

    buttons.append(InlineKeyboardButton('Увімкнути', callback_data='schedule_on'))
    buttons.append(InlineKeyboardButton('Вимкнути', callback_data='schedule_off'))

    kb.add(*buttons)
    return kb


def chat_settings_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    buttons = list()

    buttons.append(InlineKeyboardButton('Налаштування розсилки', callback_data='chat_schedule'))
    buttons.append(InlineKeyboardButton('Вимкнути чи увімкнути бота', callback_data='chat_status'))

    kb.add(*buttons)
    return kb


def bot_status_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    buttons = list()

    buttons.append(InlineKeyboardButton('Увімкнути', callback_data='bot_on'))
    buttons.append(InlineKeyboardButton('Вимкнути', callback_data='bot_off'))

    kb.add(*buttons)
    return kb

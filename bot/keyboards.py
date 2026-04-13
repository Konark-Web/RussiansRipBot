from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHART_CATEGORIES = [
    ("personnel_units_inc", "Особовий склад"),
    ("tanks_inc", "Танки"),
    ("armoured_fighting_vehicles_inc", "ББМ"),
    ("artillery_systems_inc", "Арт. системи"),
    ("mlrs_inc", "РСЗВ"),
    ("aa_warfare_systems_inc", "Засоби ППО"),
    ("planes_inc", "Літаки"),
    ("helicopters_inc", "Гелікоптери"),
    ("vehicles_fuel_tanks_inc", "Автотехніка"),
    ("warships_cutters_inc", "Кораблі та катери"),
    ("cruise_missiles_inc", "Крилаті ракети"),
    ("uav_systems_inc", "БПЛА"),
    ("special_military_equip_inc", "Спец. техніка"),
    ("submarines_inc", "Підводні човни"),
]


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


def chart_categories_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(label, callback_data=f"chart:{field}")
        for field, label in CHART_CATEGORIES
    ]
    kb.add(*buttons)
    return kb


def chart_years_keyboard(field: str, years: list[int]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=4)
    buttons = [
        InlineKeyboardButton(str(year), callback_data=f"chart_year:{field}:{year}")
        for year in years
    ]
    kb.add(*buttons)
    return kb


def admin_bulk_review_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            "Тестова відправка мені", callback_data="adm_bulk:test"
        ),
        InlineKeyboardButton("Розіслати всім", callback_data="adm_bulk:send"),
        InlineKeyboardButton("Скасувати", callback_data="adm_bulk:cancel"),
    )
    return kb

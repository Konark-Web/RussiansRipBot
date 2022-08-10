import logging

from aiogram import types, Dispatcher

from bot.db.models import Chat, User
from bot.keyboards import schedule_keyboard, bot_status_keyboard

log = logging.getLogger(__name__)


async def change_schedule_user(call: types.CallbackQuery):
    new_status = call.data.split('_')[-1]

    if new_status == 'on':
        new_status = True
        status_text = 'Увімкнено'
    else:
        new_status = False
        status_text = 'Вимкнено'

    db_session = call.bot.get("db")
    async with db_session() as session:
        user: User = await session.get(User, call.from_user.id)
        user.schedule_status = new_status

        await session.commit()

    await call.message.edit_text(f'Ви змінили статус щоденної розсилки на <b>{status_text}</b>')


async def change_schedule_chat(call: types.CallbackQuery):
    new_status = call.data.split('_')[-1]

    if new_status == 'on':
        new_status = True
        status_text = 'Увімкнено'
    else:
        new_status = False
        status_text = 'Вимкнено'

    db_session = call.bot.get("db")
    async with db_session() as session:
        chat: Chat = await session.get(Chat, call.message.chat.id)
        chat.schedule_status = new_status

        await session.commit()

    await call.message.edit_text(
        f'Ви змінили статус щоденної розсилки на <b>{status_text}</b>')


async def chat_settings(call: types.CallbackQuery):
    db_session = call.bot.get("db")
    async with db_session() as session:
        chat: Chat = await session.get(Chat, call.message.chat.id)

    if call.data.split('_')[-1] == 'schedule':
        if chat.schedule_status:
            schedule_status = 'Увімкнено'
        else:
            schedule_status = 'Вимкнено'

        await call.message.edit_text(
            f'Налаштуй щоденну розсилку приємних новин у вигляді статистики.\n\n'
            f'<b>Зараз:</b> {schedule_status}')
        await call.message.edit_reply_markup(schedule_keyboard())
    else:
        if chat.status:
            status = 'Увімкнено'
        else:
            status = 'Вимкнено'

        await call.message.edit_text(
            f'Хочеш вимкнути тимчасово бота щоб не видаляти з чату? Це можна зробити. '
            f'Не буде розсилок, а команди перестануть працювати.\n\n'
            f'<b>Зараз:</b> {status}')
        await call.message.edit_reply_markup(bot_status_keyboard())


async def change_status(call: types.CallbackQuery):
    new_status = call.data.split('_')[-1]

    if new_status == 'on':
        new_status = True
    else:
        new_status = False

    db_session = call.bot.get("db")
    async with db_session() as session:
        chat: Chat = await session.get(Chat, call.message.chat.id)
        chat.status = new_status

        await session.commit()

    if new_status:
        await call.message.edit_text(f'Я повернувся і знову буду тішити вас '
                                     f'статистикою проданих квитків на концерт Кобзона')
    else:
        await call.message.edit_text(f'До скорих зустрічів! Не забувайте донатити ЗСУ!')


def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(change_schedule_user,
                                       lambda c: c.data.startswith('schedule_'),
                                       chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(change_schedule_chat,
                                       lambda c: c.data.startswith('schedule_'),
                                       is_admin=True,
                                       chat_type=[types.ChatType.GROUP,
                                                  types.ChatType.SUPERGROUP]
                                       )
    dp.register_callback_query_handler(chat_settings,
                                       lambda c: c.data.startswith('chat_'),
                                       is_admin=True)
    dp.register_callback_query_handler(change_status,
                                       lambda c: c.data.startswith('bot_'),
                                       is_admin=True)

import logging
import time

from aiogram import types, Dispatcher
from sqlalchemy import select

from bot.db.models import Chat, User
from bot.keyboards import schedule_keyboard, chat_settings_keyboard
from bot.api import get_stat_from_api

from apscheduler.schedulers.asyncio import AsyncIOScheduler

log = logging.getLogger(__name__)


async def cmd_start(message: types.Message):
    await message.answer(f'Привіт, {message.from_user.first_name}!\n'
                         f'"Я кожного дня можу надсилати статистику по русні '
                         f'яка зробила жест доброї волі та стала "хорошими русскими". '
                         f'Також можеш додати мене до чатику з друз\'ями та отримувати '
                         f'кожного вечора гарні новини 😁 \n\n'
                         f'Слава ЗСУ! 🇺🇦')

    db_session = message.bot.get("db")
    async with db_session() as session:
        user = await session.get(User, {"user_id": message.from_user.id})

        if user:
            await message.answer(f'Ви вже зареєстровані.\n'
                                 f'Якщо хочете змінити налаштування, введіть /settings')
        else:
            await session.merge(User(user_id=message.from_user.id, schedule_status=False))
            await session.commit()

            await message.answer_animation('https://i.imgur.com/AHFxtrN.mp4')
            await message.answer(f'Якщо хочете увімкнути щоденне надсилання статистики, введіть /settings')


async def settings_user(message: types.Message):
    db_session = message.bot.get("db")
    async with db_session() as session:
        user: User = await session.get(User, {"user_id": message.from_user.id})

    if user.schedule_status:
        schedule_status = 'Увімкнено'
    else:
        schedule_status = 'Вимкнено'

    await message.answer(f'Налаштуй щоденну розсилку приємних новин у вигляді статистики.\n\n'
                         f'<b>Зараз:</b> {schedule_status}',
                         reply_markup=schedule_keyboard())


async def settings_chat(message: types.Message):
    db_session = message.bot.get("db")
    async with db_session() as session:
        chat: Chat = await session.get(Chat, {"chat_id": message.chat.id})

    if chat.schedule_status:
        schedule_status = 'Увімкнено'
    else:
        schedule_status = 'Вимкнено'

    if chat.status:
        status = 'Увімкнено'
    else:
        status = 'Вимкнено'

    await message.answer(f'Ви можете увімкнути чи вимкнути щоденную розсилку статистики, '
                         f'або тимчасово вимкнути бота в чаті (щоб не видаляти його) \n\n'
                         f'<b>Щоденна розсилка:</b> {schedule_status}\n'
                         f'<b>Статус бота:</b> {status}',
                         reply_markup=chat_settings_keyboard())


async def output_stats(message: types.Message):
    stats_text = get_stat_from_api()

    await message.answer(stats_text)


async def output_about(message: types.Message):
    await message.answer('Russians Rip ☠️ - бот для публікації актуальної '
                         'статистики по втратам росії. Бота можна додати '
                         'до чату та отримувати кожного вечора гарні новини.\n\n'
                         'Не забувайте донатити на ЗСУ -> '
                         '<a href="https://send.monobank.ua/jar/2AwsVyDJ6Q">Задонатити</a>\n'
                         'Автор бота: @Konark96')


async def output_help(message: types.Message):
    await message.answer('/about - Про бота\n'
                         '/help - Список команд\n'
                         '/settings - Налаштування бота\n'
                         '/rip_stat - Статистика "хороших русских"\n\n'
                         'Якщо знайшли баг, пишіть @Konark96')


async def output_donate(message: types.Message):
    await message.answer('Підтримайте ЗСУ та наблизьте нашу перемогу!\n\n'
                         'БФ Сергія Притули - <a href="https://prytulafoundation.org/uk/home/support_page">Задонатити</a>\n'
                         'БФ Повернись живим - <a href="https://savelife.in.ua/donate/">Задонатити</a>\n'
                         'Мінцифри України - <a href="https://donate.thedigital.gov.ua/">Задонатити</a>\n'
                         'Спец рахунок НБУ - <a href="https://bank.gov.ua/ua/about/support-the-armed-forces">Задонатити</a>')


async def output_stats_by_cron(dp: Dispatcher):
    stats_text = get_stat_from_api()
    db_session = dp.bot.get("db")

    sql_chat = select(Chat).where(Chat.status == True, Chat.schedule_status == True)
    sql_user = select(User).where(User.schedule_status == True)
    async with db_session() as session:
        chat_request = await session.execute(sql_chat)
        chats = chat_request.scalars()

        user_request = await session.execute(sql_user)
        users = user_request.scalars()

    for chat in chats:
        try:
            await dp.bot.send_message(chat.chat_id, stats_text)
            time.sleep(0.1)
        except Exception as e:
            log.exception(e)

    for user in users:
        try:
            await dp.bot.send_message(user.user_id, stats_text)
            time.sleep(0.1)
        except Exception as e:
            log.exception(e)


def register_commands(dp: Dispatcher):
    dp.register_message_handler(cmd_start, chat_type=types.ChatType.PRIVATE, commands="start")
    dp.register_message_handler(settings_user, chat_type=types.ChatType.PRIVATE, commands="settings")
    dp.register_message_handler(settings_chat,
                                is_admin=True,
                                chat_type=[types.ChatType.GROUP,
                                           types.ChatType.SUPERGROUP],
                                commands="settings")
    dp.register_message_handler(output_stats, commands="rip_stat")
    dp.register_message_handler(output_about, commands="about")
    dp.register_message_handler(output_help, commands="help")
    dp.register_message_handler(output_donate, commands="donate")


def schedule_jobs(scheduler: AsyncIOScheduler, dp: Dispatcher):
    scheduler.add_job(output_stats_by_cron, "cron", hour=18, minute=0, args=(dp,))
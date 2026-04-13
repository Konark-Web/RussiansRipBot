import logging

from aiogram import types, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.db.models import User
from bot.db.repositories import ChatRepository, UserRepository
from bot.db.repositories.statistics_repository import StatisticsRepository
from bot.keyboards import chat_settings_keyboard, chart_categories_keyboard, schedule_keyboard

log = logging.getLogger(__name__)


class CommandsHandler:
    def __init__(self, chat_repo: ChatRepository, user_repo: UserRepository):
        self._chats = chat_repo
        self._users = user_repo

    async def cmd_start(self, message: types.Message):
        await message.answer(
            f"Привіт, {message.from_user.first_name}!\n"
            f'\"Я кожного дня можу надсилати статистику по русні '
            f'яка зробила жест доброї волі та стала \"хорошими русскими\". '
            f'Також можеш додати мене до чатику з друз\'ями та отримувати '
            f'кожного вечора гарні новини 😁 \n\n'
            f"Слава ЗСУ! 🇺🇦"
        )

        db_session = message.bot["db"]
        async with db_session() as session:
            user = await self._users.get(session, message.from_user.id)

            if user:
                await message.answer(
                    "Ви вже зареєстровані.\n"
                    "Якщо хочете змінити налаштування, введіть /settings"
                )
            else:
                await self._users.merge(
                    session, User(user_id=message.from_user.id, schedule_status=True)
                )
                await session.commit()

                await message.answer_animation("https://i.imgur.com/AHFxtrN.mp4")
                await message.answer(
                    "Щоденна розсилка статистики за замовчуванням <b>увімкнена</b>. "
                    "Вимкнути або знову увімкнути можна в /settings.",
                    parse_mode="HTML",
                )

    async def settings_user(self, message: types.Message):
        db_session = message.bot["db"]
        async with db_session() as session:
            user = await self._users.get(session, message.from_user.id)

        if user and user.schedule_status:
            schedule_status = "Увімкнено"
        else:
            schedule_status = "Вимкнено"

        await message.answer(
            f"Налаштуй щоденну розсилку приємних новин у вигляді статистики.\n\n"
            f"<b>Зараз:</b> {schedule_status}",
            reply_markup=schedule_keyboard(),
        )

    async def settings_chat(self, message: types.Message):
        db_session = message.bot["db"]
        async with db_session() as session:
            chat = await self._chats.get(session, message.chat.id)

        if chat and chat.schedule_status:
            schedule_status = "Увімкнено"
        else:
            schedule_status = "Вимкнено"

        if chat and chat.status:
            status = "Увімкнено"
        else:
            status = "Вимкнено"

        await message.answer(
            f"Ви можете увімкнути чи вимкнути щоденную розсилку статистики, "
            f"або тимчасово вимкнути бота в чаті (щоб не видаляти його) \n\n"
            f"<b>Щоденна розсилка:</b> {schedule_status}\n"
            f"<b>Статус бота:</b> {status}",
            reply_markup=chat_settings_keyboard(),
        )

    async def output_stats(self, message: types.Message):
        db_session = message.bot["db"]
        stats_service = message.bot["statistics_service"]

        async with db_session() as session:
            max_inc = await StatisticsRepository().get_max_increments(session)

        stats_text = await stats_service.fetch_daily_message_html(max_inc)
        await message.answer(stats_text)

    async def output_weekly_stats(self, message: types.Message):
        stats = message.bot["statistics_service"]
        stats_text = await stats.fetch_weekly_message_html()
        await message.answer(stats_text)

    async def output_records(self, message: types.Message):
        db_session = message.bot["db"]
        stats_service = message.bot["statistics_service"]

        async with db_session() as session:
            records = await StatisticsRepository().get_records(session)

        text = stats_service.format_records_html(records)
        await message.answer(text)

    async def output_average(self, message: types.Message):
        db_session = message.bot["db"]
        stats_service = message.bot["statistics_service"]

        async with db_session() as session:
            averages = await StatisticsRepository().get_averages(session)

        text = stats_service.format_averages_html(averages)
        await message.answer(text)

    async def output_chart(self, message: types.Message):
        await message.answer(
            "Оберіть категорію для графіку по роках:",
            reply_markup=chart_categories_keyboard(),
        )

    async def output_milestones(self, message: types.Message):
        db_session = message.bot["db"]
        stats_service = message.bot["statistics_service"]

        async with db_session() as session:
            totals = await StatisticsRepository().get_latest_totals(session)
            avg_inc = await StatisticsRepository().get_avg_increments_last_days(session, days=30)

        text = stats_service.format_milestones_html(totals, avg_inc)
        await message.answer(text)

    async def output_about(self, message: types.Message):
        db_session = message.bot["db"]
        async with db_session() as session:
            chat_count = await self._chats.count(session)
            user_count = await self._users.count(session)

        await message.answer(
            f'Russians Rip ☠️ - бот для публікації актуальної '
            f"статистики по втратам росії. Бота можна додати "
            f"до чату та отримувати кожного вечора гарні новини.\n\n"
            f"<b>Статистика:</b>\n"
            f"Користувачів: {user_count}\n"
            f"Чатів: {chat_count}\n\n"
            f"Не забувайте донатити на ЗСУ -> "
            f'<a href="https://send.monobank.ua/jar/2AwsVyDJ6Q">Задонатити</a>\n'
            f"Автор бота: @Konark96"
        )

    async def output_help(self, message: types.Message):
        await message.answer(
            "/about - Про бота\n"
            "/help - Список команд\n"
            "/settings - Налаштування бота\n"
            '/rip_stat - Статистика "хороших русских" за сьогодні\n'
            "/week - Тижневий звіт\n"
            "/records - Рекорди за весь час\n"
            "/average - Середні втрати за день\n"
            "/chart - Графік втрат по роках\n"
            "/milestones - Прогноз до ювілейних цифр\n\n"
            "Якщо знайшли баг, пишіть @Konark96"
        )

    async def output_donate(self, message: types.Message):
        await message.answer(
            "Підтримайте ЗСУ та наблизьте нашу перемогу!\n\n"
            "БФ Сергія Притули - <a href=\"https://prytulafoundation.org/uk/home/support_page\">Задонатити</a>\n"
            'БФ Повернись живим - <a href="https://savelife.in.ua/donate/">Задонатити</a>\n'
            'Мінцифри України - <a href="https://donate.thedigital.gov.ua/">Задонатити</a>\n'
            'Спец рахунок НБУ - <a href="https://bank.gov.ua/ua/about/support-the-armed-forces">Задонатити</a>'
        )


def schedule_jobs(scheduler: AsyncIOScheduler, dp: Dispatcher):
    broadcast = dp.bot["broadcast_service"]
    scheduler.add_job(
        broadcast.run_scheduled_statistics_broadcast,
        "cron",
        hour=9,
        minute=20,
        args=(dp,),
    )


def register_commands(dp: Dispatcher, chat_repo: ChatRepository, user_repo: UserRepository):
    handler = CommandsHandler(chat_repo, user_repo)

    dp.register_message_handler(handler.cmd_start, chat_type=types.ChatType.PRIVATE, commands="start")
    dp.register_message_handler(
        handler.settings_user, chat_type=types.ChatType.PRIVATE, commands="settings"
    )
    dp.register_message_handler(
        handler.settings_chat,
        is_admin=True,
        chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
        commands="settings",
    )
    dp.register_message_handler(handler.output_stats, commands="rip_stat", is_turned=True)
    dp.register_message_handler(handler.output_weekly_stats, commands="week", is_turned=True)
    dp.register_message_handler(handler.output_records, commands="records", is_turned=True)
    dp.register_message_handler(handler.output_average, commands="average", is_turned=True)
    dp.register_message_handler(handler.output_chart, commands="chart", is_turned=True)
    dp.register_message_handler(handler.output_milestones, commands="milestones", is_turned=True)
    dp.register_message_handler(handler.output_about, commands="about", is_turned=True)
    dp.register_message_handler(handler.output_help, commands="help", is_turned=True)
    dp.register_message_handler(handler.output_donate, commands="donate", is_turned=True)

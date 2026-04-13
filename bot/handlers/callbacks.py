import logging

from aiogram import types, Dispatcher

from bot.db.models import User
from bot.db.repositories import ChatRepository, UserRepository
from bot.db.repositories.statistics_repository import StatisticsRepository
from bot.keyboards import bot_status_keyboard, chart_years_keyboard, schedule_keyboard, CHART_CATEGORIES

log = logging.getLogger(__name__)


class CallbacksHandler:
    def __init__(self, chat_repo: ChatRepository, user_repo: UserRepository):
        self._chats = chat_repo
        self._users = user_repo

    async def change_schedule_user(self, call: types.CallbackQuery):
        new_status = call.data.split("_")[-1]

        if new_status == "on":
            new_status = True
            status_text = "Увімкнено"
        else:
            new_status = False
            status_text = "Вимкнено"

        db_session = call.bot["db"]
        async with db_session() as session:
            await self._users.merge(
                session, User(user_id=call.from_user.id, schedule_status=new_status)
            )
            await session.commit()

        await call.message.edit_text(
            f"Ви змінили статус щоденної розсилки на <b>{status_text}</b>"
        )

    async def change_schedule_chat(self, call: types.CallbackQuery):
        new_status = call.data.split("_")[-1]

        if new_status == "on":
            new_status = True
            status_text = "Увімкнено"
        else:
            new_status = False
            status_text = "Вимкнено"

        db_session = call.bot["db"]
        async with db_session() as session:
            chat = await self._chats.get(session, call.message.chat.id)
            if chat:
                chat.schedule_status = new_status
            await session.commit()

        await call.message.edit_text(
            f"Ви змінили статус щоденної розсилки на <b>{status_text}</b>"
        )

    async def chat_settings(self, call: types.CallbackQuery):
        db_session = call.bot["db"]
        async with db_session() as session:
            chat = await self._chats.get(session, call.message.chat.id)

        if call.data.split("_")[-1] == "schedule":
            if chat and chat.schedule_status:
                schedule_status = "Увімкнено"
            else:
                schedule_status = "Вимкнено"

            await call.message.edit_text(
                f"Налаштуй щоденну розсилку приємних новин у вигляді статистики.\n\n"
                f"<b>Зараз:</b> {schedule_status}"
            )
            await call.message.edit_reply_markup(schedule_keyboard())
        else:
            if chat and chat.status:
                status = "Увімкнено"
            else:
                status = "Вимкнено"

            await call.message.edit_text(
                f"Хочеш вимкнути тимчасово бота щоб не видаляти з чату? Це можна зробити. "
                f"Не буде розсилок, а команди перестануть працювати.\n\n"
                f"<b>Зараз:</b> {status}"
            )
            await call.message.edit_reply_markup(bot_status_keyboard())

    async def change_status(self, call: types.CallbackQuery):
        new_status = call.data.split("_")[-1]

        if new_status == "on":
            new_status = True
        else:
            new_status = False

        db_session = call.bot["db"]
        async with db_session() as session:
            chat = await self._chats.get(session, call.message.chat.id)
            if chat:
                chat.status = new_status
            await session.commit()

        if new_status:
            await call.message.edit_text(
                f"Я повернувся і знову буду тішити вас "
                f"статистикою проданих квитків на концерт Кобзона"
            )
        else:
            await call.message.edit_text(
                f"До скорих зустрічей! Не забувайте донатити ЗСУ!"
            )


    async def show_chart_years(self, call: types.CallbackQuery):
        """Step 1: category selected → show year buttons."""
        field = call.data.split(":", 1)[1]
        label = next((lbl for f, lbl in CHART_CATEGORIES if f == field), field)

        db_session = call.bot["db"]
        async with db_session() as session:
            years = await StatisticsRepository().get_available_years(session)

        await call.answer()
        await call.message.edit_text(
            f"<b>📊 {label}</b>\nОберіть рік:",
            reply_markup=chart_years_keyboard(field, years),
        )

    async def show_chart_monthly(self, call: types.CallbackQuery):
        """Step 2: year selected → generate monthly line chart."""
        _, field, year_str = call.data.split(":")
        year = int(year_str)
        label = next((lbl for f, lbl in CHART_CATEGORIES if f == field), field)

        await call.answer()
        await call.message.answer("⏳ Генерую графік...")

        db_session = call.bot["db"]
        chart_service = call.bot["chart_service"]

        async with db_session() as session:
            monthly_data = await StatisticsRepository().get_monthly_stats(session, field, year)

        if not monthly_data:
            await call.message.answer("Дані відсутні.")
            return

        buf = chart_service.generate_monthly_chart(label, year, monthly_data)
        await call.message.answer_photo(buf, caption=f"<b>📊 {label} — {year}</b>")


def register_callbacks(dp: Dispatcher, chat_repo: ChatRepository, user_repo: UserRepository):
    handler = CallbacksHandler(chat_repo, user_repo)

    dp.register_callback_query_handler(
        handler.change_schedule_user,
        lambda c: c.data.startswith("schedule_"),
        chat_type=types.ChatType.PRIVATE,
    )
    dp.register_callback_query_handler(
        handler.change_schedule_chat,
        lambda c: c.data.startswith("schedule_"),
        is_admin=True,
        chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
    )
    dp.register_callback_query_handler(
        handler.chat_settings,
        lambda c: c.data.startswith("chat_"),
        is_admin=True,
    )
    dp.register_callback_query_handler(
        handler.change_status,
        lambda c: c.data.startswith("bot_"),
        is_admin=True,
    )
    dp.register_callback_query_handler(
        handler.show_chart_years,
        lambda c: c.data.startswith("chart:"),
    )
    dp.register_callback_query_handler(
        handler.show_chart_monthly,
        lambda c: c.data.startswith("chart_year:"),
    )

import asyncio
import logging

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.db.repositories import ChatRepository, UserRepository
from bot.db.repositories.statistics_repository import StatisticsRepository
from bot.services.statistics_service import StatisticsService

log = logging.getLogger(__name__)

CRON_THROTTLE_SEC = 0.05


class BroadcastService:
    def __init__(
        self,
        session_factory: async_sessionmaker,
        chats: ChatRepository,
        users: UserRepository,
        statistics: StatisticsService,
    ):
        self._session_factory = session_factory
        self._chats = chats
        self._users = users
        self._statistics = statistics

    async def run_scheduled_statistics_broadcast(self, dp: Dispatcher) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                max_inc = await StatisticsRepository().get_max_increments(session)
                chats = await self._chats.list_scheduled_broadcast_targets(session)
                users = await self._users.list_scheduled_broadcast_targets(session)

        stats_text = await self._statistics.fetch_daily_message_html(max_inc)
        bot: Bot = dp.bot

        for chat in chats:
            try:
                await bot.send_message(chat.chat_id, stats_text, parse_mode="HTML")
            except Exception:
                log.exception("scheduled stats to chat %s failed", chat.chat_id)
            await asyncio.sleep(CRON_THROTTLE_SEC)

        for user in users:
            try:
                await bot.send_message(user.user_id, stats_text, parse_mode="HTML")
            except Exception:
                log.exception("scheduled stats to user %s failed", user.user_id)
            await asyncio.sleep(CRON_THROTTLE_SEC)

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.db.repositories import ChatRepository, UserRepository

log = logging.getLogger(__name__)

BROADCAST_THROTTLE_SEC = 0.05


@dataclass(frozen=True)
class OutgoingBroadcastPayload:
    text_html: str
    photo_file_id: Optional[str] = None


class BulkMessagingService:
    def __init__(
        self,
        session_factory: async_sessionmaker,
        chats: ChatRepository,
        users: UserRepository,
    ):
        self._session_factory = session_factory
        self._chats = chats
        self._users = users

    async def send_to_recipient(
        self, bot: Bot, telegram_chat_id: int, payload: OutgoingBroadcastPayload
    ) -> None:
        await self._send_one(bot, telegram_chat_id, payload)

    async def broadcast_to_all_active(self, bot: Bot, payload: OutgoingBroadcastPayload) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                chats = await self._chats.list_active_for_bulk(session)
                users = await self._users.list_all(session)

        for chat in chats:
            try:
                await self._send_one(bot, chat.chat_id, payload)
            except Exception:
                log.exception("bulk send to chat %s failed", chat.chat_id)
            await asyncio.sleep(BROADCAST_THROTTLE_SEC)

        for user in users:
            try:
                await self._send_one(bot, user.user_id, payload)
            except Exception:
                log.exception("bulk send to user %s failed", user.user_id)
            await asyncio.sleep(BROADCAST_THROTTLE_SEC)

    async def _send_one(self, bot: Bot, chat_id: int, payload: OutgoingBroadcastPayload) -> None:
        if payload.photo_file_id:
            await bot.send_photo(
                chat_id,
                payload.photo_file_id,
                caption=payload.text_html or None,
                parse_mode="HTML",
            )
        else:
            await bot.send_message(chat_id, payload.text_html, parse_mode="HTML")

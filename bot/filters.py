import logging
from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from bot.db.repositories import ChatRepository

log = logging.getLogger(__name__)

_chats = ChatRepository()


class IsAdmin(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        if hasattr(obj, "chat"):
            chat_id = obj.chat.id
        else:
            chat_id = obj.message.chat.id

        member = await obj.bot.get_chat_member(chat_id, obj.from_user.id)

        return member.is_chat_admin() == self.is_admin


class IsTurnedOn(BoundFilter):
    key = "is_turned"

    def __init__(self, is_turned):
        self.is_turned = is_turned

    async def check(self, message: types.Message):
        if message.chat.type == "private":
            return True
        chat_id = message.chat.id
        db_session = message.bot["db"]
        async with db_session() as session:
            chat = await _chats.get(session, chat_id)
            if chat is None:
                return True
            return bool(chat.status)

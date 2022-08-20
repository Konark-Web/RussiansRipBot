import logging

from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from typing import Union

from bot.db.models import Chat

log = logging.getLogger(__name__)


class IsAdmin(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        if hasattr(obj, 'chat'):
            chat_id = obj.chat.id
        else:
            chat_id = obj.message.chat.id

        member = await obj.bot.get_chat_member(chat_id, obj.from_user.id)

        return member.is_chat_admin() == self.is_admin


class IsTurnedOn(BoundFilter):
    key = 'is_turned'

    def __init__(self, is_turned):
        self.is_turned = is_turned

    async def check(self,message: types.Message):
        if message.chat.type == 'private':
            return True
        else:
            chat_id = message.chat.id
            db_session = message.bot.get("db")
            async with db_session() as session:
                chat: Chat = await session.get(Chat, {"chat_id": chat_id})

                return chat.status

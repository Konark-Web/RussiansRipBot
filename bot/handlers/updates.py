import logging

from aiogram import types, Dispatcher

from bot.db.models import Chat
from bot.db.repositories import ChatRepository

log = logging.getLogger(__name__)


class UpdatesHandler:
    def __init__(self, chat_repo: ChatRepository):
        self._chats = chat_repo

    async def chat_status(self, update: types.ChatMemberUpdated):
        log.info(update)
        db_session = update.bot["db"]

        if update.new_chat_member.status == "left":
            async with db_session() as session:
                chat = await self._chats.get(session, update.chat.id)
                if chat:
                    chat.status = False
                await session.commit()

            return

        await update.bot.send_message(
            update.chat.id,
            f"Привіт, всім! Радий приєднатися до {update.chat.title}!\n"
            f"Я кожного дня буду надсилати в чат статистику по русні "
            f'яка зробила жест доброї волі та стала "хорошими русскими" 😁\n\n'
            f"Слава ЗСУ! 🇺🇦",
        )
        await update.bot.send_animation(
            update.chat.id, "https://i.imgur.com/AHFxtrN.mp4"
        )

        async with db_session() as session:
            await self._chats.merge(session, Chat(chat_id=update.chat.id))
            await session.commit()

    async def migrate_to_supergroup(self, message: types.Message):
        db_session = message.bot["db"]

        async with db_session() as session:
            chat = await self._chats.get(session, message.migrate_from_chat_id)
            if chat:
                chat.chat_id = message.chat.id
            await session.commit()

        await message.bot.send_message(
            message.chat.id,
            f"Ваша група тепер стала супер-групою, але все добре, я це позначив собі.\n\n"
            f"Слава Україні!",
        )


def register_updates(dp: Dispatcher, chat_repo: ChatRepository):
    handler = UpdatesHandler(chat_repo)
    dp.register_my_chat_member_handler(handler.chat_status)
    dp.register_message_handler(
        handler.migrate_to_supergroup, content_types=types.ContentType.MIGRATE_FROM_CHAT_ID
    )

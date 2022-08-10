import logging

from aiogram import types, Dispatcher

from bot.db.models import Chat

log = logging.getLogger(__name__)


async def chat_status(update: types.ChatMemberUpdated):
    log.info(update)
    db_session = update.bot.get("db")

    if update.new_chat_member.status == 'left':
        async with db_session() as session:
            chat: Chat = await session.get(Chat, {'chat_id': update.chat.id})
            chat.status = False

            await session.commit()

        return

    await update.bot.send_message(update.chat.id,
                                  f'Привіт, всім! Радий приєднатися до {update.chat.title}!\n'
                                  f'Я кожного дня буду надсилати в чат статистику по русні '
                                  f'яка зробила жест доброї волі та стала "хорошими русскими" 😁\n\n'
                                  f'Слава ЗСУ! 🇺🇦')
    await update.bot.send_animation(update.chat.id, 'https://i.imgur.com/AHFxtrN.mp4')

    async with db_session() as session:
        await session.merge(Chat(chat_id=update.chat.id))
        await session.commit()


async def migrate_to_supergroup(message: types.Message):
    db_session = message.bot.get("db")

    async with db_session() as session:
        chat: Chat = await session.get(Chat, {'chat_id': message.migrate_from_chat_id})
        chat.chat_id = message.chat.id

        await session.commit()

    await message.bot.send_message(message.chat.id,
                                   f'Ваша група тепер стала супер-групою, але все добре, я це позначив собі.\n\n'
                                   f'Слава Україні!')


def register_updates(dp: Dispatcher):
    dp.register_my_chat_member_handler(chat_status)
    dp.register_message_handler(migrate_to_supergroup, content_types=types.ContentType.MIGRATE_FROM_CHAT_ID)

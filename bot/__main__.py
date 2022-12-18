import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeDefault
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from bot.config_loader import Config, load_config
from bot.db.base import Base
from bot.handlers.commands import register_commands, schedule_jobs
from bot.handlers.callbacks import register_callbacks
from bot.handlers.updates import register_updates
from bot.updatesworker import get_handled_updates_list
from bot.filters import IsAdmin, IsTurnedOn

from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="about", description="Про бота"),
        BotCommand(command="help", description="Список команд"),
        BotCommand(command="settings", description="Налаштування бота"),
        BotCommand(command="rip_stat", description="Статистика \"хороших русских\"")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    config: Config = load_config()
    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.db_name}",
        future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # expire_on_commit=False will prevent attributes from being expired
    # after commit.
    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    bot = Bot(config.bot.token, parse_mode="HTML")
    bot["db"] = async_sessionmaker
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    scheduler = AsyncIOScheduler()

    dp.filters_factory.bind(IsAdmin)
    dp.filters_factory.bind(IsTurnedOn)

    register_commands(dp)
    register_callbacks(dp)
    register_updates(dp)

    schedule_jobs(scheduler, dp)

    await set_bot_commands(bot)

    try:
        scheduler.start()
        await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logging.error("Bot stopped!")

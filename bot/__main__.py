import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.exc import ProgrammingError

from bot.config_loader import Config, load_config
from bot.db.database import create_engine_and_session_factory
from bot.db.repositories import ChatRepository, UserRepository, StatisticsRepository
from bot.db.seeder import run_seeder
from bot.filters import IsAdmin, IsTurnedOn
from bot.handlers.admin_bulk import register_admin_bulk
from bot.handlers.callbacks import register_callbacks
from bot.handlers.commands import register_commands, schedule_jobs
from bot.handlers.updates import register_updates
from bot.services import BroadcastService, BulkMessagingService, ChartService, StatisticsService
from bot.updatesworker import get_handled_updates_list

# Add root directory to sys.path for Alembic if needed
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="about", description="Про бота"),
        BotCommand(command="help", description="Список команд"),
        BotCommand(command="settings", description="Налаштування бота"),
        BotCommand(command="rip_stat", description='Статистика "хороших русских" за сьогодні'),
        BotCommand(command="week", description="Тижневий звіт"),
        BotCommand(command="records", description="Рекорди за весь час"),
        BotCommand(command="average", description="Середні втрати за день"),
        BotCommand(command="chart", description="Графік втрат по роках"),
        BotCommand(command="milestones", description="Прогноз до ювілейних цифр"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def initialize_statistics(session_factory):
    """Check if statistics table is empty and run seeder if needed."""
    async with session_factory() as session:
        repo = StatisticsRepository()
        try:
            count = await repo.get_count(session)
            if count == 0:
                logging.info("Statistics table is empty. Running seeder...")
                await run_seeder()
            else:
                logging.info(f"Statistics table has {count} records. Skipping seeding.")
        except ProgrammingError as e:
            logging.warning(f"Statistics table not found or error occurred: {e}. Please ensure migrations are applied.")
        except Exception as e:
            logging.error(f"Error during statistics initialization: {e}")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    config: Config = load_config()
    
    # 1. engine creation
    engine, session_factory = await create_engine_and_session_factory(config)

    # 2. Check and fill statistics history
    await initialize_statistics(session_factory)

    bot = Bot(config.bot.token, parse_mode="HTML")
    bot["db"] = session_factory
    bot["config"] = config

    chat_repo = ChatRepository()
    user_repo = UserRepository()
    statistics_service = StatisticsService()
    chart_service = ChartService()
    broadcast_service = BroadcastService(
        session_factory, chat_repo, user_repo, statistics_service
    )
    bulk_messaging_service = BulkMessagingService(
        session_factory, chat_repo, user_repo
    )

    bot["statistics_service"] = statistics_service
    bot["chart_service"] = chart_service
    bot["broadcast_service"] = broadcast_service
    bot["bulk_messaging_service"] = bulk_messaging_service

    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    scheduler = AsyncIOScheduler()

    dp.filters_factory.bind(IsAdmin)
    dp.filters_factory.bind(IsTurnedOn)

    register_commands(dp, chat_repo, user_repo)
    register_callbacks(dp, chat_repo, user_repo)
    register_updates(dp, chat_repo)
    register_admin_bulk(dp, bulk_messaging_service, config)

    schedule_jobs(scheduler, dp)

    await set_bot_commands(bot)

    try:
        scheduler.start()
        await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
    finally:
        await engine.dispose()
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")

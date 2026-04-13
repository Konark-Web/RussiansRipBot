from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from bot.config_loader import Config


async def create_engine_and_session_factory(config: Config):
    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.db_name}",
    )

    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    return engine, session_factory

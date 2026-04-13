from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User


class UserRepository:
    async def get(self, session: AsyncSession, user_id: int) -> Optional[User]:
        return await session.get(User, user_id)

    async def merge(self, session: AsyncSession, user: User) -> User:
        merged = await session.merge(user)
        return merged

    async def count(self, session: AsyncSession) -> int:
        stmt = select(func.count()).select_from(User)
        result = await session.execute(stmt)
        return int(result.scalar_one())

    async def list_scheduled_broadcast_targets(
        self, session: AsyncSession
    ) -> Sequence[User]:
        stmt = select(User).where(User.schedule_status.is_(True))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def list_all(self, session: AsyncSession) -> Sequence[User]:
        stmt = select(User)
        result = await session.execute(stmt)
        return result.scalars().all()

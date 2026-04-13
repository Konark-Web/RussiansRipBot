from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Chat


class ChatRepository:
    async def get(self, session: AsyncSession, chat_id: int) -> Optional[Chat]:
        return await session.get(Chat, chat_id)

    async def merge(self, session: AsyncSession, chat: Chat) -> Chat:
        merged = await session.merge(chat)
        return merged

    async def list_scheduled_broadcast_targets(
        self, session: AsyncSession
    ) -> Sequence[Chat]:
        stmt = select(Chat).where(
            Chat.status.is_(True), Chat.schedule_status.is_(True)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def list_active_for_bulk(self, session: AsyncSession) -> Sequence[Chat]:
        stmt = select(Chat).where(Chat.status.is_(True))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def count(self, session: AsyncSession) -> int:
        stmt = select(func.count()).select_from(Chat)
        result = await session.execute(stmt)
        return int(result.scalar_one())

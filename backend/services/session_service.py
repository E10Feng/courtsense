"""
Session service — session CRUD helpers
"""
from datetime import date, timedelta
from uuid import UUID
from typing import Optional
from sqlalchemy import select
from backend.database import Session as DBSession, async_session


async def get_user_sessions(user_id: UUID, days: int = 7) -> list[DBSession]:
    cutoff = date.today() - timedelta(days=days)
    async with async_session() as db:
        result = await db.execute(
            select(DBSession)
            .where(DBSession.user_id == user_id)
            .where(DBSession.date >= cutoff)
            .order_by(DBSession.date.desc())
        )
        return list(result.scalars().all())

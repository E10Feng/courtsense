"""
Session CRUD router
"""
from datetime import datetime, date, timedelta
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import Session as DBSession, async_session
from backend.models import SessionCreate, SessionResponse, SessionListResponse

router = APIRouter()


@router.post("", response_model=SessionResponse)
async def create_session(payload: SessionCreate):
    async with async_session() as db:
        db_session = DBSession(
            user_id=UUID(payload.user_id),
            sport=payload.sport,
            date=date.today(),
            score=payload.score,
            partner_names=payload.partner_names or "",
            opponent_names=payload.opponent_names or "",
            drills_done=payload.drills_done or "",
            energy=payload.energy,
            mood=payload.mood,
            legs=payload.legs,
            notes=payload.notes or "",
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        return SessionResponse(
            id=str(db_session.id),
            user_id=str(db_session.user_id),
            sport=db_session.sport,
            date=db_session.date,
            score=db_session.score,
            partner_names=db_session.partner_names,
            opponent_names=db_session.opponent_names,
            drills_done=db_session.drills_done,
            energy=db_session.energy,
            mood=db_session.mood,
            legs=db_session.legs,
            notes=db_session.notes,
            created_at=db_session.created_at,
        )


@router.get("/{user_id}", response_model=SessionListResponse)
async def get_sessions(
    user_id: str,
    days: int = Query(default=7, ge=1, le=365),
):
    async with async_session() as db:
        cutoff = date.today() - timedelta(days=days)
        result = await db.execute(
            select(DBSession)
            .where(DBSession.user_id == UUID(user_id))
            .where(DBSession.date >= cutoff)
            .order_by(DBSession.date.desc())
        )
        rows = result.scalars().all()
        return SessionListResponse(
            sessions=[
                SessionResponse(
                    id=str(s.id),
                    user_id=str(s.user_id),
                    sport=s.sport,
                    date=s.date,
                    score=s.score,
                    partner_names=s.partner_names,
                    opponent_names=s.opponent_names,
                    drills_done=s.drills_done,
                    energy=s.energy,
                    mood=s.mood,
                    legs=s.legs,
                    notes=s.notes,
                    created_at=s.created_at,
                )
                for s in rows
            ]
        )

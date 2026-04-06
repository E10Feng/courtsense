"""
Weekly digest router — triggers LangGraph digest agent
"""
import json
from datetime import date, timedelta
from uuid import UUID
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import Session as DBSession, WeeklyDigest, async_session
from backend.models import DigestGenerateRequest, DigestResponse, WeaknessItem, DrillRecommendation
from backend.services.digest_agent import generate_digest_graph

router = APIRouter()


@router.post("/generate", response_model=DigestResponse)
async def generate_digest(payload: DigestGenerateRequest):
    uid = UUID(payload.user_id)
    week_end = date.today()
    week_start = week_end - timedelta(days=6)

    async with async_session() as db:
        # Fetch sessions for the week
        result = await db.execute(
            select(DBSession)
            .where(DBSession.user_id == uid)
            .where(DBSession.date >= week_start)
            .where(DBSession.date <= week_end)
            .order_by(DBSession.date)
        )
        sessions = result.scalars().all()

        if not sessions:
            raise HTTPException(status_code=404, detail="No sessions found for this week")

        sessions_data = [
            {
                "id": str(s.id),
                "sport": s.sport,
                "date": str(s.date),
                "score": s.score,
                "partner_names": s.partner_names,
                "opponent_names": s.opponent_names,
                "drills_done": s.drills_done,
                "energy": s.energy,
                "mood": s.mood,
                "legs": s.legs,
                "notes": s.notes,
            }
            for s in sessions
        ]

        # Run LangGraph digest agent
        digest_result = await generate_digest_graph(sessions_data)

        # Store digest
        db_digest = WeeklyDigest(
            user_id=uid,
            week_start=week_start,
            week_end=week_end,
            sessions_count=len(sessions),
            weakness_summary=digest_result.get("weakness_summary"),
            top_weaknesses=digest_result.get("top_weaknesses", []),
            drill_recommendations=digest_result.get("drill_recommendations", []),
        )
        db.add(db_digest)
        await db.commit()
        await db.refresh(db_digest)

        return DigestResponse(
            id=str(db_digest.id),
            user_id=str(db_digest.user_id),
            week_start=db_digest.week_start,
            week_end=db_digest.week_end,
            sessions_count=db_digest.sessions_count,
            weakness_summary=db_digest.weakness_summary,
            top_weaknesses=[WeaknessItem(**w) for w in (db_digest.top_weaknesses or [])],
            drill_recommendations=[DrillRecommendation(**d) for d in (db_digest.drill_recommendations or [])],
            created_at=db_digest.created_at,
        )


@router.get("/{user_id}", response_model=DigestResponse)
async def get_latest_digest(user_id: str):
    uid = UUID(user_id)
    async with async_session() as db:
        result = await db.execute(
            select(WeeklyDigest)
            .where(WeeklyDigest.user_id == uid)
            .order_by(WeeklyDigest.created_at.desc())
            .limit(1)
        )
        d = result.scalar_one_or_none()
        if not d:
            raise HTTPException(status_code=404, detail="No digest found")
        return DigestResponse(
            id=str(d.id),
            user_id=str(d.user_id),
            week_start=d.week_start,
            week_end=d.week_end,
            sessions_count=d.sessions_count,
            weakness_summary=d.weakness_summary,
            top_weaknesses=[WeaknessItem(**w) for w in (d.top_weaknesses or [])],
            drill_recommendations=[DrillRecommendation(**dr) for dr in (d.drill_recommendations or [])],
            created_at=d.created_at,
        )

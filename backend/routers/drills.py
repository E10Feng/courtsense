"""
Drill search router with pgvector similarity
"""
from fastapi import APIRouter, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import Drill, async_session
from backend.models import DrillResponse, DrillSearchResponse

router = APIRouter()

# Top drills per sport, pre-seeded
SEED_DRILLS = [
    # Pickleball — beginner/intermediate
    {"sport": "pickleball", "name": "Dink Circle", "description": "Players stand at the NVZ line and hit dinks back and forth, moving laterally along the net.", "target_weakness": "net play", "reps": "20-30", "sets": "3-4", "difficulty": "beginner"},
    {"sport": "pickleball", "name": "Third Shot Drop Drill", "description": "Serve returner hits a deep return; server practices the third shot drop into the kitchen.", "target_weakness": "third shot drive", "reps": "15-20", "sets": "3", "difficulty": "intermediate"},
    {"sport": "pickleball", "name": "Serve & Return Practice", "description": "Practice 10 serves then 10 returns, tracking errors on each side.", "target_weakness": "serve placement", "reps": "10 each", "sets": "3", "difficulty": "beginner"},
    {"sport": "pickleball", "name": "Lane Footwork Drills", "description": "Side-to-side shuffles through cones placed at court width, focusing on ready position.", "target_weakness": "footwork", "reps": "10-15 lengths", "sets": "3", "difficulty": "beginner"},
    {"sport": "pickleball", "name": "Lob Recovery", "description": "Partner hits lobs; practice the overhead smash and defensive lobs from deep court.", "target_weakness": "overhead smash", "reps": "10-15", "sets": "3", "difficulty": "intermediate"},
    {"sport": "pickleball", "name": "Two-Bounce Rule Game", "description": "Play mini-singles games enforcing the two-bounce rule strictly; focus on groundstrokes.", "target_weakness": "groundstroke consistency", "reps": "20 min", "sets": "1", "difficulty": "intermediate"},
    {"sport": "pickleball", "name": "Kitchen Rules Volley", "description": "Service games with emphasis on no-volley-zone violations; track foot faults.", "target_weakness": "net play", "reps": "30 min", "sets": "1", "difficulty": "beginner"},
    {"sport": "pickleball", "name": "Spin Serve Rotation", "description": "Practice topspin and backspin serves with targets in opposite corners.", "target_weakness": "serve variety", "reps": "20", "sets": "3", "difficulty": "intermediate"},
    {"sport": "pickleball", "name": "Cut Shot Drill", "description": "Partner feeds balls to the middle; practice cutting them cross-court vs down-the-line.", "target_weakness": "shot selection", "reps": "15 each", "sets": "3", "difficulty": "intermediate"},
    {"sport": "pickleball", "name": "Pickleball Yoga (Balance)", "description": "Single-leg stance rallies to failure; improves balance and反应速度.", "target_weakness": "balance", "reps": "until failure", "sets": "3", "difficulty": "beginner"},
    # Tennis — beginner/intermediate
    {"sport": "tennis", "name": "Cross-Court Rally", "description": "Two players rally cross-court from the baseline, aiming for 20+ shot rallies.", "target_weakness": "groundstroke consistency", "reps": "20 rallies", "sets": "4", "difficulty": "beginner"},
    {"sport": "tennis", "name": "Serve Target Practice", "description": "Place cones in service boxes; serve until 8/10 land in targets.", "target_weakness": "serve accuracy", "reps": "50", "sets": "2", "difficulty": "beginner"},
    {"sport": "tennis", "name": "Inside-Out Forehand", "description": "Coach feeds balls to the backhand side; player attacks with inside-out forehand.", "target_weakness": "forehand winners", "reps": "15-20", "sets": "3", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "Two-Handed Backhand Block", "description": "Practice blocking returns of fast serves using the two-handed backhand.", "target_weakness": "backhand return", "reps": "20", "sets": "3", "difficulty": "beginner"},
    {"sport": "tennis", "name": "Approach Shot + Volley", "description": "Player approaches the net after a deep approach shot, finishes with a volley.", "target_weakness": "net game", "reps": "10-15", "sets": "3", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "Slice Serve Build-Up", "description": "Start with flat serves, add slice, then kick; track ace and error rates.", "target_weakness": "serve variety", "reps": "30", "sets": "2", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "Split-Step Timing", "description": "Coach feeds balls at random intervals; player practices split-step timing before each shot.", "target_weakness": "footwork", "reps": "20", "sets": "3", "difficulty": "beginner"},
    {"sport": "tennis", "name": "Down-the-Line Challenge", "description": "Rally down-the-line only; errors or nets count as points.", "target_weakness": "down-the-line shots", "reps": "15 points", "sets": "3", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "Tactical Serve Return", "description": "Returner practices returning to specific targets based on server's position.", "target_weakness": "return placement", "reps": "20", "sets": "3", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "High-Ball Overhead Smash", "description": "Coach tosses high balls; practice overhead smashes with proper footwork.", "target_weakness": "overhead smash", "reps": "15", "sets": "3", "difficulty": "intermediate"},
]


@router.get("/search", response_model=DrillSearchResponse)
async def search_drills(
    query: str = Query(..., min_length=1),
    sport: str = Query(default=None, pattern="^(pickleball|tennis)$"),
    limit: int = Query(default=5, ge=1, le=20),
):
    """
    pgvector similarity search on drill embeddings.
    Falls back to keyword filtering if embeddings aren't set up.
    """
    async with async_session() as db:
        stmt = select(Drill).where(Drill.embedding.isnot(None))
        if sport:
            stmt = stmt.where(Drill.sport == sport)
        stmt = stmt.order_by(Drill.embedding.l2_distance(_get_query_embedding(query))).limit(limit)
        
        result = await db.execute(stmt)
        rows = result.scalars().all()

        # Fallback: if no embeddings, use LIKE search
        if not rows:
            stmt = select(Drill)
            if sport:
                stmt = stmt.where(Drill.sport == sport)
            stmt = stmt.where(
                (Drill.name.ilike(f"%{query}%")) |
                (Drill.target_weakness.ilike(f"%{query}%")) |
                (Drill.description.ilike(f"%{query}%"))
            ).limit(limit)
            result = await db.execute(stmt)
            rows = result.scalars().all()

        return DrillSearchResponse(
            drills=[
                DrillResponse(
                    id=str(d.id),
                    sport=d.sport,
                    name=d.name,
                    description=d.description,
                    target_weakness=d.target_weakness,
                    reps=d.reps,
                    sets=d.sets,
                    difficulty=d.difficulty,
                )
                for d in rows
            ]
        )


def _get_query_embedding(query: str) -> list:
    """Placeholder: returns a zero vector. Real impl uses OpenAI/minimax embedding."""
    return [0.0] * 1536

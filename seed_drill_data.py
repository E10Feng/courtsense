"""
Seed drill data — run once to populate the drills table.
Usage: python seed_drill_data.py
"""
import asyncio
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Drill, engine, Base, async_session
from backend.services.embedding_service import embed_drills


PICKLEBALL_DRILLS = [
    {"sport": "pickleball", "name": "Dink Circle", "description": "Players stand at the NVZ line and hit controlled dinks back and forth, moving laterally along the net.", "target_weakness": "net play", "reps": "20-30", "sets": "3-4", "difficulty": "beginner"},
    {"sport": "pickleball", "name": "Third Shot Drop Drill", "description": "Serve returner hits a deep return; server practices the third shot drop into the kitchen.", "target_weakness": "third shot drive", "reps": "15-20", "sets": "3", "difficulty": "intermediate"},
    {"sport": "pickleball", "name": "Serve & Return Practice", "description": "Practice 10 serves then 10 returns, tracking errors on each side.", "target_weakness": "serve placement", "reps": "10 each", "sets": "3", "difficulty": "beginner"},
    {"sport": "pickleball", "name": "Lane Footwork Drills", "description": "Side-to-side shuffles through cones placed at court width, focusing on ready position.", "target_weakness": "footwork", "reps": "10-15 lengths", "sets": "3", "difficulty": "beginner"},
    {"sport": "pickleball", "name": "Lob Recovery", "description": "Partner hits lobs; practice the overhead smash and defensive lobs from deep court.", "target_weakness": "overhead smash", "reps": "10-15", "sets": "3", "difficulty": "intermediate"},
    {"sport": "pickleball", "name": "Two-Bounce Groundstroke Rally", "description": "Play mini-singles games enforcing the two-bounce rule strictly; focus on groundstrokes.", "target_weakness": "groundstroke consistency", "reps": "20 min", "sets": "1", "difficulty": "intermediate"},
    {"sport": "pickleball", "name": "NVZ Volley Count", "description": "Service games with emphasis on volleying at the net; track volley-to-error ratio.", "target_weakness": "net play", "reps": "30 min", "sets": "1", "difficulty": "beginner"},
    {"sport": "pickleball", "name": "Spin Serve Rotation", "description": "Practice topspin and backspin serves with targets in opposite corners.", "target_weakness": "serve variety", "reps": "20", "sets": "3", "difficulty": "intermediate"},
    {"sport": "pickleball", "name": "Cut Shot vs Down-the-Line", "description": "Partner feeds balls to the middle; practice cutting them cross-court vs going down-the-line.", "target_weakness": "shot selection", "reps": "15 each", "sets": "3", "difficulty": "intermediate"},
    {"sport": "pickleball", "name": "Balance Stance Rally", "description": "Single-leg stance rallies to failure; improves balance and reaction speed.", "target_weakness": "balance", "reps": "until failure", "sets": "3", "difficulty": "beginner"},
    {"sport": "pickleball", "name": "Erne Practice", "description": "Practice the erne shot — approaching the net from the sideline after a partner's return.", "target_weakness": "erne shot", "reps": "10-15", "sets": "3", "difficulty": "advanced"},
    {"sport": "pickleball", "name": "Around the Post", "description": "Practice hitting around-the-post lobs and shots when opponent dominates the middle.", "target_weakness": "around the post", "reps": "10-15", "sets": "3", "difficulty": "advanced"},
]

TENNIS_DRILLS = [
    {"sport": "tennis", "name": "Cross-Court Rally", "description": "Two players rally cross-court from the baseline, aiming for 20+ shot rallies.", "target_weakness": "groundstroke consistency", "reps": "20 rallies", "sets": "4", "difficulty": "beginner"},
    {"sport": "tennis", "name": "Serve Target Practice", "description": "Place cones in service boxes; serve until 8/10 land in targets.", "target_weakness": "serve accuracy", "reps": "50", "sets": "2", "difficulty": "beginner"},
    {"sport": "tennis", "name": "Inside-Out Forehand", "description": "Coach feeds balls to the backhand side; player attacks with inside-out forehand.", "target_weakness": "forehand winners", "reps": "15-20", "sets": "3", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "Two-Handed Backhand Block", "description": "Practice blocking returns of fast serves using the two-handed backhand.", "target_weakness": "backhand return", "reps": "20", "sets": "3", "difficulty": "beginner"},
    {"sport": "tennis", "name": "Approach + Volley", "description": "Player approaches the net after a deep approach shot, finishes with a volley.", "target_weakness": "net game", "reps": "10-15", "sets": "3", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "Slice Serve Build-Up", "description": "Start with flat serves, add slice, then kick; track ace and error rates.", "target_weakness": "serve variety", "reps": "30", "sets": "2", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "Split-Step Timing", "description": "Coach feeds balls at random intervals; player practices split-step timing before each shot.", "target_weakness": "footwork", "reps": "20", "sets": "3", "difficulty": "beginner"},
    {"sport": "tennis", "name": "Down-the-Line Challenge", "description": "Rally down-the-line only; errors or nets count as points.", "target_weakness": "down-the-line shots", "reps": "15 points", "sets": "3", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "Tactical Serve Return", "description": "Returner practices returning to specific targets based on server's position.", "target_weakness": "return placement", "reps": "20", "sets": "3", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "High-Ball Overhead Smash", "description": "Coach tosses high balls; practice overhead smashes with proper footwork.", "target_weakness": "overhead smash", "reps": "15", "sets": "3", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "One-Handed Backhand Slice", "description": "Practice the one-handed backhand slice for low balls outside the body.", "target_weakness": "backhand slice", "reps": "20", "sets": "3", "difficulty": "intermediate"},
    {"sport": "tennis", "name": "Kick Serve Practice", "description": "Practice kick serves with high toss, brushing up the back of the ball; land in service box.", "target_weakness": "kick serve", "reps": "30", "sets": "2", "difficulty": "advanced"},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    all_drills = PICKLEBALL_DRILLS + TENNIS_DRILLS
    print(f"Seeding {len(all_drills)} drills with embeddings...")
    enriched = await embed_drills(all_drills)

    async with async_session() as db:
        for drill_data in enriched:
            embedding = drill_data.pop("embedding", None)
            drill = Drill(**drill_data, embedding=embedding)
            db.add(drill)
        await db.commit()
    print(f"Seeded {len(all_drills)} drills successfully.")


if __name__ == "__main__":
    asyncio.run(seed())

"""Database setup for CourtSense — PostgreSQL + pgvector."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Date, ForeignKey
from sqlalchemy.types import UserDefinedType
import uuid

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/courtsense"
)

engine = create_engine(DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2"))
AsyncSessionLocal = None

try:
    import asyncpg
    import asyncio
    async def get_async_engine():
        global AsyncSessionLocal
        pool = await asyncpg.create_pool(DATABASE_URL.replace("postgresql+asyncpg", "postgresql://"), min_size=1, max_size=10)
        AsyncSessionLocal = sessionmaker(pool, expire_on_commit=False)
        return pool
except Exception:
    pass

Base = declarative_base()


class Vector(UserDefinedType):
    """pgvector type for SQLAlchemy."""
    cache_ok = True

    def get_col_spec(self):
        return "vector(1536)"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            return f"[{','.join(str(v) for v in value)}]"
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            import re
            nums = re.findall(r"[-e.0-9]+", value)
            return [float(n) for n in nums]
        return process


class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    sport = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    score = Column(String(50), nullable=False)
    partner_names = Column(String(255), default="")
    opponent_names = Column(String(255), default="")
    drills_done = Column(String(255), default="")
    energy = Column(Integer, nullable=False)
    mood = Column(Integer, nullable=False)
    legs = Column(Integer, nullable=False)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class WeeklyDigestModel(Base):
    __tablename__ = "weekly_digests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)
    sessions_count = Column(Integer, nullable=False)
    weakness_summary = Column(Text, nullable=True)
    top_weaknesses = Column(JSON, default=[])
    drill_recommendations = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)


class DrillModel(Base):
    __tablename__ = "drills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sport = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    target_weakness = Column(String(100), nullable=False)
    reps = Column(String(20), nullable=False)
    sets = Column(String(20), nullable=False)
    difficulty = Column(String(20), nullable=False)
    embedding = Column(Vector(), nullable=True)


from datetime import datetime


def init_db():
    """Create all tables."""
    Base.metadata.create_all(engine)

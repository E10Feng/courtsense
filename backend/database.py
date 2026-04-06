"""
PostgreSQL + pgvector database setup
"""
import os
from sqlalchemy import Column, String, Integer, Float, Text, Date, DateTime, ForeignKey, create_engine, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSON, VECTOR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import uuid as uuid_lib

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/courtsense"
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())


class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    sport = Column(String, nullable=False)  # "pickleball" | "tennis"
    date = Column(Date, nullable=False)
    score = Column(String, nullable=False)
    partner_names = Column(String, default="")
    opponent_names = Column(String, default="")
    drills_done = Column(String, default="")
    energy = Column(Integer, default=3)  # 1-5
    mood = Column(Integer, default=3)    # 1-5
    legs = Column(Integer, default=3)    # 1-5
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.utcnow())


class WeeklyDigest(Base):
    __tablename__ = "weekly_digests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)
    sessions_count = Column(Integer, default=0)
    weakness_summary = Column(Text, nullable=True)
    top_weaknesses = Column(JSON, default=list)
    drill_recommendations = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())


class Drill(Base):
    __tablename__ = "drills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    sport = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    target_weakness = Column(String, nullable=False)
    reps = Column(String, nullable=False)
    sets = Column(String, nullable=False)
    difficulty = Column(String, default="intermediate")
    # pgvector embedding column — 1536 dims for OpenAI/text-embedding-3-small
    embedding = Column(VECTOR(dim=1536), nullable=True)


from datetime import datetime

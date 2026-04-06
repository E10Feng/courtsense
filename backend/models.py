"""Pydantic models for CourtSense."""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str
    email: str


class User(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime


class SessionCreate(BaseModel):
    user_id: UUID
    sport: str = Field(..., pattern="^(pickleball|tennis)$")
    date: Optional[date] = None
    score: str
    partner_names: Optional[str] = ""
    opponent_names: Optional[str] = ""
    drills_done: Optional[str] = ""
    energy: int = Field(..., ge=1, le=5)
    mood: int = Field(..., ge=1, le=5)
    legs: int = Field(..., ge=1, le=5)
    notes: Optional[str] = ""


class Session(BaseModel):
    id: UUID
    user_id: UUID
    sport: str
    date: date
    score: str
    partner_names: str
    opponent_names: str
    drills_done: str
    energy: int
    mood: int
    legs: int
    notes: str
    created_at: datetime


class SessionResponse(BaseModel):
    id: str
    user_id: str
    sport: str
    date: date
    score: str
    partner_names: str
    opponent_names: str
    drills_done: str
    energy: int
    mood: int
    legs: int
    notes: str
    created_at: datetime


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]


class WeeklyDigestCreate(BaseModel):
    user_id: UUID


class WeaknessItem(BaseModel):
    area: str
    percent: float
    evidence: str


class DrillRecommendation(BaseModel):
    drill: str
    why: str
    reps: str
    sets: str
    target_weakness: str


class WeeklyDigest(BaseModel):
    id: UUID
    user_id: UUID
    week_start: date
    week_end: date
    sessions_count: int
    weakness_summary: str
    top_weaknesses: List[WeaknessItem]
    drill_recommendations: List[DrillRecommendation]
    created_at: datetime


class DigestGenerateRequest(BaseModel):
    user_id: UUID


class DigestGenerateResponse(BaseModel):
    digest_id: UUID
    weakness_summary: str
    top_weaknesses: List[WeaknessItem]
    drill_recommendations: List[DrillRecommendation]


class DigestResponse(BaseModel):
    id: str
    user_id: str
    week_start: date
    week_end: date
    sessions_count: int
    weakness_summary: str
    top_weaknesses: List[WeaknessItem]
    drill_recommendations: List[DrillRecommendation]
    created_at: datetime


class Drill(BaseModel):
    id: UUID
    sport: str
    name: str
    description: str
    target_weakness: str
    reps: str
    sets: str
    difficulty: str


class DrillSearchResponse(BaseModel):
    drills: List[Drill]

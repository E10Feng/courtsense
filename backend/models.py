"""
Pydantic models for CourtSense
"""
import uuid
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    user_id: str
    sport: str = Field(..., pattern="^(pickleball|tennis)$")
    score: str
    partner_names: Optional[str] = ""
    opponent_names: Optional[str] = ""
    drills_done: Optional[str] = ""
    energy: int = Field(1, ge=1, le=5)
    mood: int = Field(3, ge=1, le=5)
    legs: int = Field(3, ge=1, le=5)
    notes: Optional[str] = ""


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
    sessions: list[SessionResponse]


class DigestGenerateRequest(BaseModel):
    user_id: str


class WeaknessItem(BaseModel):
    area: str
    percent: float
    evidence: str


class DrillRecommendation(BaseModel):
    drill: str
    why: str
    reps: str
    sets: str


class DigestResponse(BaseModel):
    id: str
    user_id: str
    week_start: date
    week_end: date
    sessions_count: int
    weakness_summary: Optional[str]
    top_weaknesses: list[WeaknessItem]
    drill_recommendations: list[DrillRecommendation]
    created_at: datetime


class DrillResponse(BaseModel):
    id: str
    sport: str
    name: str
    description: str
    target_weakness: str
    reps: str
    sets: str
    difficulty: str


class DrillSearchResponse(BaseModel):
    drills: list[DrillResponse]

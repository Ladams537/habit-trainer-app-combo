from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# --- Skill schemas ---

class SkillCreate(BaseModel):
    name: str
    category: str = "general"
    sub_skills: list[str] = Field(default_factory=list)
    current_level: str = "beginner"


class SkillUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    sub_skills: list[str] | None = None
    current_level: str | None = None


class SkillResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    category: str
    sub_skills: list[str]
    current_level: str
    total_practice_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Practice session schemas ---

class PracticeSessionCreate(BaseModel):
    duration_minutes: int = Field(ge=1)
    quality_rating: int = Field(ge=1, le=5)
    focus_area: str | None = None
    notes: str | None = None


class PracticeSessionResponse(BaseModel):
    id: UUID
    skill_id: UUID
    duration_minutes: int
    quality_rating: int
    focus_area: str | None
    notes: str | None
    practiced_at: datetime

    model_config = {"from_attributes": True}


# --- Competency level schemas ---

class CompetencyLevelResponse(BaseModel):
    id: UUID
    skill_id: UUID
    sub_skill: str
    difficulty: float
    stability: float
    last_review_date: datetime | None
    next_review_date: datetime | None
    review_count: int
    retrievability: float = 0.0

    model_config = {"from_attributes": True}


# --- Progress / Schedule / Today schemas ---

class SkillProgressResponse(BaseModel):
    skill: SkillResponse
    competency_levels: list[CompetencyLevelResponse]
    recent_sessions: list[PracticeSessionResponse]


class SubSkillSchedule(BaseModel):
    sub_skill: str
    next_review_date: datetime | None
    retrievability: float
    is_due: bool


class SkillScheduleResponse(BaseModel):
    skill: SkillResponse
    schedule: list[SubSkillSchedule]


class SkillTodayResponse(BaseModel):
    id: UUID
    name: str
    category: str
    due_count: int
    total_practice_minutes: int

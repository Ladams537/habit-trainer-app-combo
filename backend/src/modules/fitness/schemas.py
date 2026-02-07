from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# --- Exercise schemas ---

class ExerciseCreate(BaseModel):
    name: str
    category: str = Field(pattern=r"^(compound|isolation|cardio)$")
    muscle_groups: list[str] = Field(default_factory=list)
    equipment: str | None = None


class ExerciseResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    name: str
    category: str
    muscle_groups: list[str]
    equipment: str | None
    is_custom: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Template schemas ---

class TemplateExerciseCreate(BaseModel):
    exercise_id: UUID
    sort_order: int = 0
    target_sets: int = 3
    target_reps: int = 10
    target_weight_kg: float | None = None
    set_type: str = "working"
    rest_seconds: int = 120


class TemplateExerciseResponse(BaseModel):
    id: UUID
    exercise_id: UUID
    sort_order: int
    target_sets: int
    target_reps: int
    target_weight_kg: float | None
    set_type: str
    rest_seconds: int
    exercise: ExerciseResponse

    model_config = {"from_attributes": True}


class WorkoutTemplateCreate(BaseModel):
    name: str
    description: str | None = None
    exercises: list[TemplateExerciseCreate] = Field(default_factory=list)


class WorkoutTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    exercises: list[TemplateExerciseCreate] | None = None


class WorkoutTemplateResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    exercises: list[TemplateExerciseResponse] = []

    model_config = {"from_attributes": True}


# --- Session schemas ---

class StartSessionRequest(BaseModel):
    template_id: UUID | None = None


class AddExerciseRequest(BaseModel):
    exercise_id: UUID


class CompleteSessionRequest(BaseModel):
    notes: str | None = None


class WorkoutSetCreate(BaseModel):
    exercise_id: UUID
    set_number: int
    weight_kg: float = 0
    reps: int = 0
    rpe: int | None = Field(default=None, ge=1, le=10)
    set_type: str = "working"
    completed: bool = True


class WorkoutSetResponse(BaseModel):
    id: UUID
    session_id: UUID
    exercise_id: UUID
    set_number: int
    weight_kg: float
    reps: int
    rpe: int | None
    set_type: str
    completed: bool
    logged_at: datetime

    model_config = {"from_attributes": True}


class ExerciseSetsGroup(BaseModel):
    exercise: ExerciseResponse
    sets: list[WorkoutSetResponse]


class WorkoutSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    template_id: UUID | None
    started_at: datetime
    completed_at: datetime | None
    notes: str | None
    status: str
    template_name: str | None = None
    exercise_groups: list[ExerciseSetsGroup] = []

    model_config = {"from_attributes": True}


class WorkoutSessionSummary(BaseModel):
    id: UUID
    template_id: UUID | None
    started_at: datetime
    completed_at: datetime | None
    status: str
    template_name: str | None = None
    exercise_count: int = 0
    total_sets: int = 0
    total_volume: float = 0


# --- Stats schemas ---

class ExerciseProgressionPoint(BaseModel):
    date: datetime
    max_weight: float
    best_set_weight: float
    best_set_reps: int
    volume: float
    sets_count: int


class ExerciseStatsResponse(BaseModel):
    exercise: ExerciseResponse
    progression: list[ExerciseProgressionPoint]
    total_sessions: int
    pr_weight: float
    total_volume: float


# --- Overview stats schemas ---

class WeeklyVolume(BaseModel):
    week_start: str
    total_volume: float
    session_count: int


class MuscleGroupVolume(BaseModel):
    muscle_group: str
    volume: float


class OverviewStatsResponse(BaseModel):
    weekly_volume: list[WeeklyVolume]
    muscle_group_volume: list[MuscleGroupVolume]
    total_workouts: int
    total_volume: float
    current_streak: int

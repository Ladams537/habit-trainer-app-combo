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
    rating_energy: int | None = Field(None, ge=1, le=5)
    rating_mood: int | None = Field(None, ge=1, le=5)


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
    rating_energy: int | None = None
    rating_mood: int | None = None

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
    rating_energy: int | None = None
    rating_mood: int | None = None


# --- Stats schemas ---


class ExerciseProgressionPoint(BaseModel):
    date: datetime
    max_weight: float
    best_set_weight: float
    best_set_reps: int
    volume: float
    sets_count: int
    estimated_1rm: float


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


# --- Program schemas ---


class ProgramExercisePrescription(BaseModel):
    exercise_id: UUID
    exercise_name: str
    sets: int = 3
    reps: int = 10
    weight_kg: float = 0
    rest_seconds: int = 120
    set_type: str = "working"


class ProgramDayPrescription(BaseModel):
    day_label: str
    template_id: UUID | None = None
    exercises: list[ProgramExercisePrescription] = Field(default_factory=list)


class ProgramWeekResponse(BaseModel):
    id: UUID
    week_number: int
    status: str
    prescriptions: list[ProgramDayPrescription]
    progression_source: str | None
    recovery_rating: int | None
    notes: str | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProgramCreate(BaseModel):
    name: str
    description: str | None = None
    workouts_per_week: int = Field(default=3, ge=1, le=7)
    template_ids: list[UUID] = Field(default_factory=list)


class ProgramUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = Field(default=None, pattern=r"^(active|completed|paused)$")


class ProgramResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: str
    workouts_per_week: int
    weeks: list[ProgramWeekResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProgramSummary(BaseModel):
    id: UUID
    name: str
    status: str
    workouts_per_week: int
    week_count: int
    current_week: int | None
    created_at: datetime


class ProgressionOption(BaseModel):
    label: str
    key: str
    prescriptions: list[ProgramDayPrescription]
    description: str


class ProgressionOptionsResponse(BaseModel):
    week_number: int
    options: list[ProgressionOption]


class CompleteWeekRequest(BaseModel):
    recovery_rating: int = Field(ge=1, le=5)
    notes: str | None = None


class AcceptProgressionRequest(BaseModel):
    option_key: str
    tweaks: list[ProgramDayPrescription] | None = None


class WeeklySummary(BaseModel):
    week_start: str
    session_count: int
    total_volume: float
    exercises_trained: list[str]
    avg_rpe: float | None
    avg_energy: float | None

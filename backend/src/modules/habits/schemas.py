from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HabitCreate(BaseModel):
    name: str
    habit_type: str = Field(pattern=r"^(boolean|numeric|duration)$")
    frequency: str = "daily"
    frequency_config: dict = Field(default_factory=dict)
    target_value: float = 1.0
    unit: str | None = None
    color: str = "#4CAF50"


class HabitUpdate(BaseModel):
    name: str | None = None
    frequency: str | None = None
    frequency_config: dict | None = None
    target_value: float | None = None
    unit: str | None = None
    color: str | None = None
    is_active: bool | None = None


class HabitResponse(BaseModel):
    id: UUID
    name: str
    habit_type: str
    frequency: str
    frequency_config: dict
    target_value: float
    unit: str | None
    color: str
    sort_order: int
    is_active: bool
    created_at: datetime
    current_streak: int = 0
    strength: float = 0.0

    model_config = {"from_attributes": True}


class HabitTodayResponse(BaseModel):
    id: UUID
    name: str
    habit_type: str
    target_value: float
    unit: str | None
    color: str
    sort_order: int
    completed_today: bool = False
    today_value: float = 0.0
    current_streak: int = 0
    strength: float = 0.0

    model_config = {"from_attributes": True}


class HabitLogCreate(BaseModel):
    value: float = 1.0
    completed: bool = True
    completed_at: date | None = None
    notes: str | None = None
    energy_level: int | None = Field(default=None, ge=1, le=10)
    mood: int | None = Field(default=None, ge=1, le=10)


class HabitCompletionResponse(BaseModel):
    id: UUID
    habit_id: UUID
    completed_at: datetime
    value: float
    completed: bool

    model_config = {"from_attributes": True}


class HabitStreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    strength: float
    completion_dates: list[date]


class ReorderRequest(BaseModel):
    habit_ids: list[UUID]

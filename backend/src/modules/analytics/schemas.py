from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel


# --- Calendar ---


class CalendarEvent(BaseModel):
    date: date
    domain: str
    event_type: str
    entity_id: str | None = None
    title: str
    subtitle: str | None = None
    color: str | None = None
    metadata: dict[str, Any] | None = None


class CalendarDay(BaseModel):
    date: date
    events: list[CalendarEvent]


class CalendarResponse(BaseModel):
    from_date: date
    to_date: date
    days: list[CalendarDay]


# --- Heatmap ---


class HeatmapDay(BaseModel):
    date: date
    count: int
    fitness_count: int
    habits_count: int
    skills_count: int


class HeatmapResponse(BaseModel):
    year: int
    days: list[HeatmapDay]


# --- Streaks ---


class StreakItem(BaseModel):
    domain: str
    name: str
    current_streak: int
    longest_streak: int
    strength: float | None = None
    entity_id: UUID | None = None


class StreaksResponse(BaseModel):
    streaks: list[StreakItem]
    total_active: int


# --- Trends ---


class TrendPoint(BaseModel):
    date: str
    value: float


class TrendSeries(BaseModel):
    metric: str
    unit: str
    data: list[TrendPoint]


class TrendsResponse(BaseModel):
    domain: str
    period_days: int
    series: list[TrendSeries]


# --- Correlations ---


class CorrelationPoint(BaseModel):
    date: str
    x_value: float
    y_value: float


class CorrelationResponse(BaseModel):
    x_label: str
    y_label: str
    correlation_coefficient: float | None
    data: list[CorrelationPoint]


# --- Insights ---


class InsightCard(BaseModel):
    id: str
    icon: str
    domain: str
    color: str
    title: str
    message: str


# --- Dashboard (combined) ---


class AnalyticsDashboardResponse(BaseModel):
    insights: list[InsightCard]
    heatmap: HeatmapResponse
    streaks: StreaksResponse

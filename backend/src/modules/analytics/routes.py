import asyncio
from datetime import date, timedelta

from fastapi import APIRouter, Query

from src.api.dependencies import DB, CurrentUser
from src.modules.analytics.schemas import (
    AnalyticsDashboardResponse,
    CalendarResponse,
    CorrelationResponse,
    HeatmapResponse,
    StreaksResponse,
    TrendsResponse,
)
from src.modules.analytics.service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_dashboard(user: CurrentUser, db: DB):
    service = AnalyticsService(db)
    insights, heatmap, streaks = await asyncio.gather(
        service.generate_insights(user.id),
        service.get_heatmap(user.id, date.today().year),
        service.get_all_streaks(user.id),
    )
    return AnalyticsDashboardResponse(
        insights=insights, heatmap=heatmap, streaks=streaks
    )


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    user: CurrentUser,
    db: DB,
    year: int = Query(default_factory=lambda: date.today().year),
):
    service = AnalyticsService(db)
    return await service.get_heatmap(user.id, year)


@router.get("/streaks", response_model=StreaksResponse)
async def get_streaks(user: CurrentUser, db: DB):
    service = AnalyticsService(db)
    return await service.get_all_streaks(user.id)


@router.get("/trends", response_model=TrendsResponse)
async def get_trends(
    user: CurrentUser,
    db: DB,
    domain: str = Query(default="fitness"),
    period: str = Query(default="90d"),
):
    period_days = int(period.rstrip("d"))
    service = AnalyticsService(db)
    return await service.get_trends(user.id, domain, period_days)


@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar(
    user: CurrentUser,
    db: DB,
    from_date: date = Query(
        alias="from",
        default_factory=lambda: date.today().replace(day=1),
    ),
    to_date: date = Query(
        alias="to",
        default_factory=lambda: (
            date.today().replace(day=1) + timedelta(days=32)
        ).replace(day=1)
        - timedelta(days=1),
    ),
):
    service = AnalyticsService(db)
    return await service.get_calendar(user.id, from_date, to_date)


@router.get("/correlations", response_model=CorrelationResponse)
async def get_correlations(
    user: CurrentUser,
    db: DB,
    x: str = Query(default="habits.completion_rate"),
    y: str = Query(default="fitness.volume"),
    period: str = Query(default="90d"),
):
    period_days = int(period.rstrip("d"))
    service = AnalyticsService(db)
    return await service.get_correlations(user.id, x, y, period_days)

from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.dependencies import DB, CurrentUser
from src.modules.habits.schemas import (
    HabitCompletionResponse,
    HabitCreate,
    HabitLogCreate,
    HabitResponse,
    HabitStreakResponse,
    HabitTodayResponse,
    HabitUpdate,
    ReorderRequest,
)
from src.modules.habits.service import HabitService, compute_habit_strength, compute_streaks

router = APIRouter(prefix="/api/habits", tags=["habits"])


async def _enrich_habit(service: HabitService, habit) -> dict:
    """Add streak and strength to a habit for response."""
    completion_dates = await service._get_completion_dates(habit.id)
    current_streak, _ = compute_streaks(completion_dates)
    strength = compute_habit_strength(completion_dates)
    return {
        **{c.key: getattr(habit, c.key) for c in habit.__table__.columns},
        "current_streak": current_streak,
        "strength": strength,
    }


@router.get("/", response_model=list[HabitResponse])
async def list_habits(user: CurrentUser, db: DB):
    service = HabitService(db)
    habits = await service.get_habits(user.id)
    return [await _enrich_habit(service, h) for h in habits]


@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(data: HabitCreate, user: CurrentUser, db: DB):
    service = HabitService(db)
    habit = await service.create_habit(user.id, data)
    return await _enrich_habit(service, habit)


@router.get("/today", response_model=list[HabitTodayResponse])
async def today_habits(user: CurrentUser, db: DB):
    service = HabitService(db)
    return await service.get_today_habits(user.id)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(habit_id: UUID, user: CurrentUser, db: DB):
    service = HabitService(db)
    habit = await service.get_habit(user.id, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return await _enrich_habit(service, habit)


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(habit_id: UUID, data: HabitUpdate, user: CurrentUser, db: DB):
    service = HabitService(db)
    habit = await service.update_habit(user.id, habit_id, data)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return await _enrich_habit(service, habit)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(habit_id: UUID, user: CurrentUser, db: DB):
    service = HabitService(db)
    if not await service.delete_habit(user.id, habit_id):
        raise HTTPException(status_code=404, detail="Habit not found")


@router.post("/{habit_id}/log", response_model=HabitCompletionResponse, status_code=status.HTTP_201_CREATED)
async def log_completion(habit_id: UUID, data: HabitLogCreate, user: CurrentUser, db: DB):
    service = HabitService(db)
    try:
        return await service.log_completion(user.id, habit_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{habit_id}/log/{target_date}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_completion(habit_id: UUID, target_date: date, user: CurrentUser, db: DB):
    service = HabitService(db)
    if not await service.remove_completion(user.id, habit_id, target_date):
        raise HTTPException(status_code=404, detail="Completion not found")


@router.get("/{habit_id}/streak", response_model=HabitStreakResponse)
async def get_streak(habit_id: UUID, user: CurrentUser, db: DB):
    service = HabitService(db)
    result = await service.get_streak(user.id, habit_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return result


@router.put("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_habits(data: ReorderRequest, user: CurrentUser, db: DB):
    service = HabitService(db)
    await service.reorder_habits(user.id, data.habit_ids)

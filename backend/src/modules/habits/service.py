from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.habits.models import ActivityLog, HabitCompletion, HabitDefinition
from src.modules.habits.schemas import HabitCreate, HabitLogCreate, HabitUpdate


def compute_habit_strength(completions: list[date]) -> float:
    """Loop-style habit strength: exponential moving average, alpha=0.07."""
    if not completions:
        return 0.0

    alpha = 0.07
    strength = 0.0
    completion_set = set(completions)

    start = min(completions)
    current = start
    today = date.today()

    while current <= today:
        if current in completion_set:
            strength = strength + alpha * (1.0 - strength)
        else:
            strength = strength * (1 - alpha)
        current += timedelta(days=1)

    return round(strength, 4)


def compute_streaks(completions: list[date]) -> tuple[int, int]:
    """Return (current_streak, longest_streak) from a sorted list of completion dates."""
    if not completions:
        return 0, 0

    sorted_dates = sorted(set(completions))
    today = date.today()

    # Build streaks
    streaks: list[int] = []
    current_run = 1

    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] - sorted_dates[i - 1] == timedelta(days=1):
            current_run += 1
        else:
            streaks.append(current_run)
            current_run = 1
    streaks.append(current_run)

    longest = max(streaks)

    # Current streak: count backwards from today
    current = 0
    check = today
    date_set = set(sorted_dates)
    while check in date_set:
        current += 1
        check -= timedelta(days=1)

    return current, longest


class HabitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_habit(self, user_id: UUID, data: HabitCreate) -> HabitDefinition:
        # Get max sort_order
        result = await self.db.execute(
            select(func.coalesce(func.max(HabitDefinition.sort_order), -1))
            .where(HabitDefinition.user_id == user_id)
        )
        max_order = result.scalar()

        habit = HabitDefinition(
            user_id=user_id,
            name=data.name,
            habit_type=data.habit_type,
            frequency=data.frequency,
            frequency_config=data.frequency_config,
            target_value=data.target_value,
            unit=data.unit,
            color=data.color,
            sort_order=max_order + 1,
        )
        self.db.add(habit)
        await self.db.flush()
        await self.db.refresh(habit)
        return habit

    async def get_habits(self, user_id: UUID, active_only: bool = True) -> list[HabitDefinition]:
        query = select(HabitDefinition).where(HabitDefinition.user_id == user_id)
        if active_only:
            query = query.where(HabitDefinition.is_active == True)  # noqa: E712
        query = query.order_by(HabitDefinition.sort_order)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_habit(self, user_id: UUID, habit_id: UUID) -> HabitDefinition | None:
        result = await self.db.execute(
            select(HabitDefinition)
            .where(HabitDefinition.id == habit_id, HabitDefinition.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_habit(self, user_id: UUID, habit_id: UUID, data: HabitUpdate) -> HabitDefinition | None:
        habit = await self.get_habit(user_id, habit_id)
        if not habit:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(habit, key, value)

        await self.db.flush()
        await self.db.refresh(habit)
        return habit

    async def delete_habit(self, user_id: UUID, habit_id: UUID) -> bool:
        """Soft delete: set is_active = False."""
        habit = await self.get_habit(user_id, habit_id)
        if not habit:
            return False
        habit.is_active = False
        await self.db.flush()
        return True

    def _is_due_today(self, habit: HabitDefinition) -> bool:
        today = date.today()
        if habit.frequency == "daily":
            return True
        if habit.frequency == "weekdays":
            return today.weekday() < 5
        if habit.frequency == "custom":
            config = habit.frequency_config or {}
            days = config.get("days", [])
            # ISO weekday: 1=Monday...7=Sunday
            return today.isoweekday() in days
        return True

    async def get_today_habits(self, user_id: UUID) -> list[dict]:
        habits = await self.get_habits(user_id, active_only=True)
        today_start = datetime.combine(date.today(), datetime.min.time(), tzinfo=timezone.utc)
        today_end = today_start + timedelta(days=1)

        result = []
        for habit in habits:
            if not self._is_due_today(habit):
                continue

            # Check today's completion
            comp_result = await self.db.execute(
                select(HabitCompletion)
                .where(
                    HabitCompletion.habit_id == habit.id,
                    HabitCompletion.completed_at >= today_start,
                    HabitCompletion.completed_at < today_end,
                    HabitCompletion.completed == True,  # noqa: E712
                )
            )
            today_completions = list(comp_result.scalars().all())
            completed_today = len(today_completions) > 0
            today_value = sum(float(c.value) for c in today_completions)

            # Get streak info
            completion_dates = await self._get_completion_dates(habit.id)
            current_streak, _ = compute_streaks(completion_dates)
            strength = compute_habit_strength(completion_dates)

            result.append({
                "id": habit.id,
                "name": habit.name,
                "habit_type": habit.habit_type,
                "target_value": float(habit.target_value),
                "unit": habit.unit,
                "color": habit.color,
                "sort_order": habit.sort_order,
                "completed_today": completed_today,
                "today_value": today_value,
                "current_streak": current_streak,
                "strength": strength,
            })

        return result

    async def log_completion(
        self, user_id: UUID, habit_id: UUID, data: HabitLogCreate
    ) -> HabitCompletion:
        habit = await self.get_habit(user_id, habit_id)
        if not habit:
            raise ValueError("Habit not found")

        completed_date = data.completed_at or date.today()
        completed_at = datetime.combine(
            completed_date, datetime.now(timezone.utc).time(), tzinfo=timezone.utc
        )

        # For boolean habits, replace existing completion for this day
        if habit.habit_type == "boolean":
            day_start = datetime.combine(completed_date, datetime.min.time(), tzinfo=timezone.utc)
            day_end = day_start + timedelta(days=1)
            await self.db.execute(
                delete(HabitCompletion).where(
                    HabitCompletion.habit_id == habit_id,
                    HabitCompletion.completed_at >= day_start,
                    HabitCompletion.completed_at < day_end,
                )
            )

        # Create activity log entry
        activity = ActivityLog(
            user_id=user_id,
            domain="habits",
            started_at=completed_at,
            ended_at=completed_at,
            energy_level=data.energy_level,
            mood=data.mood,
            notes=data.notes,
        )
        self.db.add(activity)
        await self.db.flush()

        completion = HabitCompletion(
            activity_id=activity.id,
            habit_id=habit_id,
            completed_at=completed_at,
            value=data.value,
            completed=data.completed,
        )
        self.db.add(completion)
        await self.db.flush()
        await self.db.refresh(completion)
        return completion

    async def remove_completion(self, user_id: UUID, habit_id: UUID, target_date: date) -> bool:
        habit = await self.get_habit(user_id, habit_id)
        if not habit:
            return False

        day_start = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        result = await self.db.execute(
            delete(HabitCompletion)
            .where(
                HabitCompletion.habit_id == habit_id,
                HabitCompletion.completed_at >= day_start,
                HabitCompletion.completed_at < day_end,
            )
            .returning(HabitCompletion.id)
        )
        deleted = result.all()
        return len(deleted) > 0

    async def _get_completion_dates(self, habit_id: UUID) -> list[date]:
        day_col = func.date_trunc("day", HabitCompletion.completed_at).label("day")
        result = await self.db.execute(
            select(day_col)
            .where(
                HabitCompletion.habit_id == habit_id,
                HabitCompletion.completed == True,  # noqa: E712
            )
            .distinct()
            .order_by(day_col)
        )
        return [row[0].date() if hasattr(row[0], "date") else row[0] for row in result.all()]

    async def get_streak(self, user_id: UUID, habit_id: UUID) -> dict | None:
        habit = await self.get_habit(user_id, habit_id)
        if not habit:
            return None

        completion_dates = await self._get_completion_dates(habit_id)
        current, longest = compute_streaks(completion_dates)
        strength = compute_habit_strength(completion_dates)

        return {
            "current_streak": current,
            "longest_streak": longest,
            "strength": strength,
            "completion_dates": completion_dates,
        }

    async def reorder_habits(self, user_id: UUID, habit_ids: list[UUID]) -> None:
        for i, habit_id in enumerate(habit_ids):
            habit = await self.get_habit(user_id, habit_id)
            if habit:
                habit.sort_order = i
        await self.db.flush()

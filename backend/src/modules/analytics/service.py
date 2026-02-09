import asyncio
import math
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.analytics.schemas import (
    CalendarDay,
    CalendarEvent,
    CalendarResponse,
    CorrelationPoint,
    CorrelationResponse,
    HeatmapDay,
    HeatmapResponse,
    InsightCard,
    StreakItem,
    StreaksResponse,
    TrendPoint,
    TrendSeries,
    TrendsResponse,
)
from src.modules.fitness.models import WorkoutProgram, WorkoutSession, WorkoutSet
from src.modules.habits.models import ActivityLog, HabitCompletion, HabitDefinition
from src.modules.habits.service import compute_habit_strength, compute_streaks
from src.modules.skills.models import PracticeSession, SkillDefinition


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ #
    #  Heatmap                                                            #
    # ------------------------------------------------------------------ #

    async def get_heatmap(self, user_id: UUID, year: int) -> HeatmapResponse:
        year_start = datetime(year, 1, 1, tzinfo=timezone.utc)
        year_end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        day_col = func.date_trunc("day", ActivityLog.started_at).label("day")
        result = await self.db.execute(
            select(day_col, ActivityLog.domain, func.count().label("cnt"))
            .where(
                ActivityLog.user_id == user_id,
                ActivityLog.started_at >= year_start,
                ActivityLog.started_at <= year_end,
            )
            .group_by(day_col, ActivityLog.domain)
        )
        rows = result.all()

        # Aggregate per day
        day_map: dict[date, dict[str, int]] = defaultdict(
            lambda: {"fitness": 0, "habits": 0, "skills": 0}
        )
        for row in rows:
            d = row.day.date() if hasattr(row.day, "date") else row.day
            day_map[d][row.domain] = row.cnt

        days = []
        for d, counts in sorted(day_map.items()):
            total = counts["fitness"] + counts["habits"] + counts["skills"]
            days.append(
                HeatmapDay(
                    date=d,
                    count=total,
                    fitness_count=counts["fitness"],
                    habits_count=counts["habits"],
                    skills_count=counts["skills"],
                )
            )

        return HeatmapResponse(year=year, days=days)

    # ------------------------------------------------------------------ #
    #  Calendar                                                           #
    # ------------------------------------------------------------------ #

    async def get_calendar(
        self, user_id: UUID, from_date: date, to_date: date
    ) -> CalendarResponse:
        from_dt = datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc)
        to_dt = datetime.combine(to_date, datetime.max.time(), tzinfo=timezone.utc)

        events: list[CalendarEvent] = []

        # 1) Fitness sessions
        sessions_result = await self.db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.started_at >= from_dt,
                WorkoutSession.started_at <= to_dt,
            )
            .options(selectinload(WorkoutSession.sets))
            .order_by(WorkoutSession.started_at)
        )
        for session in sessions_result.scalars().all():
            d = session.started_at.date() if isinstance(session.started_at, datetime) else session.started_at
            set_count = sum(1 for s in session.sets if s.completed)
            events.append(
                CalendarEvent(
                    date=d,
                    domain="fitness",
                    event_type="workout",
                    entity_id=str(session.id),
                    title=session.template_name or "Workout",
                    subtitle=f"{set_count} sets" if set_count else session.status,
                    color="#3B82F6",
                    metadata={"status": session.status},
                )
            )

        # 2) Habit completions grouped by day + habit
        day_col = func.date_trunc("day", HabitCompletion.completed_at).label("day")
        habits_result = await self.db.execute(
            select(
                HabitCompletion.habit_id,
                HabitDefinition.name,
                day_col,
                func.sum(HabitCompletion.value).label("total"),
            )
            .join(HabitDefinition, HabitDefinition.id == HabitCompletion.habit_id)
            .where(
                HabitDefinition.user_id == user_id,
                HabitCompletion.completed == True,  # noqa: E712
                HabitCompletion.completed_at >= from_dt,
                HabitCompletion.completed_at <= to_dt,
            )
            .group_by(HabitCompletion.habit_id, HabitDefinition.name, day_col)
            .order_by(day_col)
        )
        for habit_id, habit_name, day, total in habits_result.all():
            d = day.date() if hasattr(day, "date") else day
            events.append(
                CalendarEvent(
                    date=d,
                    domain="habits",
                    event_type="habit_completion",
                    entity_id=str(habit_id),
                    title=habit_name,
                    subtitle=f"{total:.0f}" if total and total > 1 else None,
                    color="#22C55E",
                )
            )

        # 3) Skill practice sessions
        practice_result = await self.db.execute(
            select(PracticeSession, SkillDefinition.name)
            .join(SkillDefinition, SkillDefinition.id == PracticeSession.skill_id)
            .where(
                SkillDefinition.user_id == user_id,
                PracticeSession.practiced_at >= from_dt,
                PracticeSession.practiced_at <= to_dt,
            )
            .order_by(PracticeSession.practiced_at)
        )
        for practice, skill_name in practice_result.all():
            d = practice.practiced_at.date() if isinstance(practice.practiced_at, datetime) else practice.practiced_at
            events.append(
                CalendarEvent(
                    date=d,
                    domain="skills",
                    event_type="practice",
                    entity_id=str(practice.skill_id),
                    title=skill_name,
                    subtitle=f"{practice.duration_minutes}min" if practice.duration_minutes else None,
                    color="#8B5CF6",
                )
            )

        # 4) Active program scheduled days (future only)
        today = date.today()
        if to_date >= today:
            programs_result = await self.db.execute(
                select(WorkoutProgram).where(
                    WorkoutProgram.user_id == user_id,
                    WorkoutProgram.status == "active",
                )
            )
            for program in programs_result.scalars().all():
                # Show a scheduled indicator for active program
                events.append(
                    CalendarEvent(
                        date=today,
                        domain="fitness",
                        event_type="program_active",
                        entity_id=str(program.id),
                        title=f"Program: {program.name}",
                        subtitle="Active",
                        color="#3B82F6",
                        metadata={"program_status": "active"},
                    )
                )

        # Group into days
        days_map: dict[date, list[CalendarEvent]] = defaultdict(list)
        for event in events:
            days_map[event.date].append(event)

        calendar_days = [
            CalendarDay(date=d, events=evts) for d, evts in sorted(days_map.items())
        ]

        return CalendarResponse(
            from_date=from_date, to_date=to_date, days=calendar_days
        )

    # ------------------------------------------------------------------ #
    #  Streaks                                                            #
    # ------------------------------------------------------------------ #

    async def get_all_streaks(self, user_id: UUID) -> StreaksResponse:
        habit_streaks = await self._habit_streaks(user_id)
        fitness_streak = await self._fitness_streak(user_id)
        skill_streaks = await self._skill_streaks(user_id)

        all_streaks = habit_streaks + fitness_streak + skill_streaks
        total_active = sum(1 for s in all_streaks if s.current_streak > 0)
        return StreaksResponse(streaks=all_streaks, total_active=total_active)

    async def _habit_streaks(self, user_id: UUID) -> list[StreakItem]:
        # Get all active habits
        habits_result = await self.db.execute(
            select(HabitDefinition).where(
                HabitDefinition.user_id == user_id,
                HabitDefinition.is_active == True,  # noqa: E712
            )
        )
        habits = list(habits_result.scalars().all())
        if not habits:
            return []

        # Split habits by partial_completion_counts setting
        partial_habits = [h for h in habits if h.partial_completion_counts]
        strict_habits = [h for h in habits if not h.partial_completion_counts]

        dates_by_habit: dict[UUID, list[date]] = defaultdict(list)
        day_col = func.date_trunc("day", HabitCompletion.completed_at).label("day")

        # Batch query for partial_completion_counts=True: any log counts
        if partial_habits:
            partial_ids = [h.id for h in partial_habits]
            comps_result = await self.db.execute(
                select(HabitCompletion.habit_id, day_col)
                .where(
                    HabitCompletion.habit_id.in_(partial_ids),
                    HabitCompletion.completed == True,  # noqa: E712
                )
                .distinct()
                .order_by(HabitCompletion.habit_id, day_col)
            )
            for habit_id, day in comps_result.all():
                d = day.date() if hasattr(day, "date") else day
                dates_by_habit[habit_id].append(d)

        # Batch query for partial_completion_counts=False: need GROUP BY + HAVING
        if strict_habits:
            strict_ids = [h.id for h in strict_habits]
            # Build a mapping of habit_id -> target_value for filtering
            target_by_id = {h.id: float(h.target_value) for h in strict_habits}

            # Query grouped sums per habit per day
            comps_result = await self.db.execute(
                select(
                    HabitCompletion.habit_id,
                    day_col,
                    func.sum(HabitCompletion.value).label("total"),
                )
                .where(
                    HabitCompletion.habit_id.in_(strict_ids),
                    HabitCompletion.completed == True,  # noqa: E712
                )
                .group_by(HabitCompletion.habit_id, day_col)
                .order_by(HabitCompletion.habit_id, day_col)
            )
            for habit_id, day, total in comps_result.all():
                d = day.date() if hasattr(day, "date") else day
                if float(total) >= target_by_id.get(habit_id, 1):
                    dates_by_habit[habit_id].append(d)

        items = []
        for habit in habits:
            completion_dates = dates_by_habit.get(habit.id, [])
            current, longest = compute_streaks(completion_dates)
            strength = compute_habit_strength(completion_dates)
            items.append(
                StreakItem(
                    domain="habits",
                    name=habit.name,
                    current_streak=current,
                    longest_streak=longest,
                    strength=strength,
                    entity_id=habit.id,
                )
            )
        return items

    async def _fitness_streak(self, user_id: UUID) -> list[StreakItem]:
        # Consecutive-week workout streak
        result = await self.db.execute(
            select(WorkoutSession.started_at)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
            )
            .order_by(WorkoutSession.started_at)
        )
        rows = result.all()
        if not rows:
            return [
                StreakItem(
                    domain="fitness",
                    name="Weekly Workouts",
                    current_streak=0,
                    longest_streak=0,
                )
            ]

        # Get unique weeks (Monday-based)
        weeks_set: set[date] = set()
        for (started_at,) in rows:
            d = started_at.date() if isinstance(started_at, datetime) else started_at
            week_start = d - timedelta(days=d.weekday())
            weeks_set.add(week_start)

        sorted_weeks = sorted(weeks_set)

        # Calculate streaks
        longest = 1
        current_run = 1
        for i in range(1, len(sorted_weeks)):
            if sorted_weeks[i] - sorted_weeks[i - 1] == timedelta(weeks=1):
                current_run += 1
                longest = max(longest, current_run)
            else:
                current_run = 1

        # Current streak: count back from this week
        this_week = date.today() - timedelta(days=date.today().weekday())
        current_streak = 0
        check = this_week
        week_set_lookup = set(sorted_weeks)
        while check in week_set_lookup:
            current_streak += 1
            check -= timedelta(weeks=1)

        return [
            StreakItem(
                domain="fitness",
                name="Weekly Workouts",
                current_streak=current_streak,
                longest_streak=longest,
            )
        ]

    async def _skill_streaks(self, user_id: UUID) -> list[StreakItem]:
        # Get active skills with their practice sessions
        skills_result = await self.db.execute(
            select(SkillDefinition).where(
                SkillDefinition.user_id == user_id,
                SkillDefinition.is_active == True,  # noqa: E712
            )
        )
        skills = list(skills_result.scalars().all())
        if not skills:
            return []

        skill_ids = [s.id for s in skills]

        # Batch query practice dates
        day_col = func.date_trunc("day", PracticeSession.practiced_at).label("day")
        prac_result = await self.db.execute(
            select(PracticeSession.skill_id, day_col)
            .where(PracticeSession.skill_id.in_(skill_ids))
            .distinct()
            .order_by(PracticeSession.skill_id, day_col)
        )
        prac_rows = prac_result.all()

        dates_by_skill: dict[UUID, list[date]] = defaultdict(list)
        for skill_id, day in prac_rows:
            d = day.date() if hasattr(day, "date") else day
            dates_by_skill[skill_id].append(d)

        items = []
        for skill in skills:
            practice_dates = dates_by_skill.get(skill.id, [])
            current, longest = compute_streaks(practice_dates)
            items.append(
                StreakItem(
                    domain="skills",
                    name=skill.name,
                    current_streak=current,
                    longest_streak=longest,
                    entity_id=skill.id,
                )
            )
        return items

    # ------------------------------------------------------------------ #
    #  Trends                                                             #
    # ------------------------------------------------------------------ #

    async def get_trends(
        self, user_id: UUID, domain: str, period_days: int = 90
    ) -> TrendsResponse:
        if domain == "fitness":
            series = await self._fitness_trends(user_id, period_days)
        elif domain == "habits":
            series = await self._habits_trends(user_id, period_days)
        elif domain == "skills":
            series = await self._skills_trends(user_id, period_days)
        else:
            series = []

        return TrendsResponse(domain=domain, period_days=period_days, series=series)

    async def _fitness_trends(
        self, user_id: UUID, period_days: int
    ) -> list[TrendSeries]:
        from_dt = datetime.combine(
            date.today() - timedelta(days=period_days),
            datetime.min.time(),
            tzinfo=timezone.utc,
        )

        result = await self.db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
                WorkoutSession.started_at >= from_dt,
            )
            .options(selectinload(WorkoutSession.sets))
            .order_by(WorkoutSession.started_at)
        )
        sessions = list(result.scalars().all())

        # Weekly bucketing
        weekly_volume: dict[str, float] = defaultdict(float)
        weekly_sessions: dict[str, int] = defaultdict(int)

        for session in sessions:
            d = (
                session.started_at.date()
                if isinstance(session.started_at, datetime)
                else session.started_at
            )
            week_start = (d - timedelta(days=d.weekday())).isoformat()
            weekly_sessions[week_start] += 1
            for ws in session.sets:
                if ws.completed:
                    weekly_volume[week_start] += ws.weight_kg * ws.reps

        all_weeks = sorted(
            set(list(weekly_volume.keys()) + list(weekly_sessions.keys()))
        )

        volume_series = TrendSeries(
            metric="volume",
            unit="kg",
            data=[
                TrendPoint(date=w, value=round(weekly_volume.get(w, 0), 1))
                for w in all_weeks
            ],
        )
        session_series = TrendSeries(
            metric="session_count",
            unit="sessions",
            data=[
                TrendPoint(date=w, value=weekly_sessions.get(w, 0)) for w in all_weeks
            ],
        )
        return [volume_series, session_series]

    async def _habits_trends(
        self, user_id: UUID, period_days: int
    ) -> list[TrendSeries]:
        today = date.today()
        start = today - timedelta(days=period_days)

        # Get active habits count over time (use current active count as approximation)
        habits_result = await self.db.execute(
            select(func.count())
            .select_from(HabitDefinition)
            .where(
                HabitDefinition.user_id == user_id,
                HabitDefinition.is_active == True,  # noqa: E712
            )
        )
        total_active = habits_result.scalar() or 1

        # Daily completions
        day_col = func.date_trunc("day", HabitCompletion.completed_at).label("day")
        comps_result = await self.db.execute(
            select(
                day_col,
                func.count(func.distinct(HabitCompletion.habit_id)).label("cnt"),
            )
            .join(HabitDefinition, HabitDefinition.id == HabitCompletion.habit_id)
            .where(
                HabitDefinition.user_id == user_id,
                HabitCompletion.completed == True,  # noqa: E712
                HabitCompletion.completed_at
                >= datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc),
            )
            .group_by(day_col)
            .order_by(day_col)
        )
        comp_rows = comps_result.all()

        data = []
        for day, cnt in comp_rows:
            d = day.date() if hasattr(day, "date") else day
            rate = round(min(cnt / total_active * 100, 100), 1)
            data.append(TrendPoint(date=d.isoformat(), value=rate))

        return [TrendSeries(metric="completion_rate", unit="%", data=data)]

    async def _skills_trends(
        self, user_id: UUID, period_days: int
    ) -> list[TrendSeries]:
        from_dt = datetime.combine(
            date.today() - timedelta(days=period_days),
            datetime.min.time(),
            tzinfo=timezone.utc,
        )

        day_col = func.date_trunc("day", PracticeSession.practiced_at).label("day")
        result = await self.db.execute(
            select(
                day_col,
                func.sum(PracticeSession.duration_minutes).label("total_mins"),
                func.avg(PracticeSession.quality_rating).label("avg_quality"),
            )
            .join(SkillDefinition, SkillDefinition.id == PracticeSession.skill_id)
            .where(
                SkillDefinition.user_id == user_id,
                PracticeSession.practiced_at >= from_dt,
            )
            .group_by(day_col)
            .order_by(day_col)
        )
        rows = result.all()

        minutes_data = []
        quality_data = []
        for day, total_mins, avg_quality in rows:
            d = day.date() if hasattr(day, "date") else day
            d_str = d.isoformat()
            minutes_data.append(TrendPoint(date=d_str, value=float(total_mins or 0)))
            quality_data.append(
                TrendPoint(date=d_str, value=round(float(avg_quality or 0), 1))
            )

        return [
            TrendSeries(metric="practice_minutes", unit="min", data=minutes_data),
            TrendSeries(metric="avg_quality", unit="rating", data=quality_data),
        ]

    # ------------------------------------------------------------------ #
    #  Correlations                                                       #
    # ------------------------------------------------------------------ #

    async def get_correlations(
        self,
        user_id: UUID,
        x_metric: str,
        y_metric: str,
        period_days: int = 90,
    ) -> CorrelationResponse:
        x_label = x_metric.replace(".", " ").replace("_", " ").title()
        y_label = y_metric.replace(".", " ").replace("_", " ").title()

        x_data = await self._get_weekly_metric(user_id, x_metric, period_days)
        y_data = await self._get_weekly_metric(user_id, y_metric, period_days)

        # JOIN on common weeks
        common_weeks = sorted(set(x_data.keys()) & set(y_data.keys()))
        points = [
            CorrelationPoint(date=w, x_value=x_data[w], y_value=y_data[w])
            for w in common_weeks
        ]

        r = self._pearson_r(
            [x_data[w] for w in common_weeks],
            [y_data[w] for w in common_weeks],
        )

        return CorrelationResponse(
            x_label=x_label,
            y_label=y_label,
            correlation_coefficient=r,
            data=points,
        )

    async def _get_weekly_metric(
        self, user_id: UUID, metric: str, period_days: int
    ) -> dict[str, float]:
        """Return {week_start_iso: value} for the given metric."""
        from_dt = datetime.combine(
            date.today() - timedelta(days=period_days),
            datetime.min.time(),
            tzinfo=timezone.utc,
        )

        if metric == "fitness.volume":
            result = await self.db.execute(
                select(WorkoutSession)
                .where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.status == "completed",
                    WorkoutSession.started_at >= from_dt,
                )
                .options(selectinload(WorkoutSession.sets))
            )
            sessions = list(result.scalars().all())
            weekly: dict[str, float] = defaultdict(float)
            for s in sessions:
                d = (
                    s.started_at.date()
                    if isinstance(s.started_at, datetime)
                    else s.started_at
                )
                w = (d - timedelta(days=d.weekday())).isoformat()
                for ws in s.sets:
                    if ws.completed:
                        weekly[w] += ws.weight_kg * ws.reps
            return {k: round(v, 1) for k, v in weekly.items()}

        elif metric == "fitness.session_count":
            result = await self.db.execute(
                select(WorkoutSession.started_at).where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.status == "completed",
                    WorkoutSession.started_at >= from_dt,
                )
            )
            rows = result.all()
            weekly = defaultdict(float)
            for (started_at,) in rows:
                d = (
                    started_at.date()
                    if isinstance(started_at, datetime)
                    else started_at
                )
                w = (d - timedelta(days=d.weekday())).isoformat()
                weekly[w] += 1
            return dict(weekly)

        elif metric == "habits.completion_rate":
            habits_result = await self.db.execute(
                select(func.count())
                .select_from(HabitDefinition)
                .where(
                    HabitDefinition.user_id == user_id,
                    HabitDefinition.is_active == True,  # noqa: E712
                )
            )
            total_active = habits_result.scalar() or 1

            day_col = func.date_trunc("day", HabitCompletion.completed_at).label("day")
            comps_result = await self.db.execute(
                select(day_col, func.count(func.distinct(HabitCompletion.habit_id)))
                .join(HabitDefinition, HabitDefinition.id == HabitCompletion.habit_id)
                .where(
                    HabitDefinition.user_id == user_id,
                    HabitCompletion.completed == True,  # noqa: E712
                    HabitCompletion.completed_at >= from_dt,
                )
                .group_by(day_col)
            )
            daily = comps_result.all()

            # Bucket into weeks: average daily rate per week
            week_rates: dict[str, list[float]] = defaultdict(list)
            for day, cnt in daily:
                d = day.date() if hasattr(day, "date") else day
                w = (d - timedelta(days=d.weekday())).isoformat()
                week_rates[w].append(min(cnt / total_active * 100, 100))

            return {w: round(sum(r) / len(r), 1) for w, r in week_rates.items()}

        elif metric == "skills.practice_minutes":
            day_col = func.date_trunc("day", PracticeSession.practiced_at).label("day")
            result = await self.db.execute(
                select(day_col, func.sum(PracticeSession.duration_minutes))
                .join(SkillDefinition, SkillDefinition.id == PracticeSession.skill_id)
                .where(
                    SkillDefinition.user_id == user_id,
                    PracticeSession.practiced_at >= from_dt,
                )
                .group_by(day_col)
            )
            daily = result.all()
            week_mins: dict[str, float] = defaultdict(float)
            for day, mins in daily:
                d = day.date() if hasattr(day, "date") else day
                w = (d - timedelta(days=d.weekday())).isoformat()
                week_mins[w] += float(mins or 0)
            return dict(week_mins)

        return {}

    @staticmethod
    def _pearson_r(x: list[float], y: list[float]) -> float | None:
        n = len(x)
        if n < 3:
            return None
        mx = sum(x) / n
        my = sum(y) / n
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        dx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
        dy = math.sqrt(sum((yi - my) ** 2 for yi in y))
        if dx == 0 or dy == 0:
            return None
        return round(num / (dx * dy), 3)

    # ------------------------------------------------------------------ #
    #  Insights                                                           #
    # ------------------------------------------------------------------ #

    async def generate_insights(self, user_id: UUID) -> list[InsightCard]:
        results = await asyncio.gather(
            self._insight_stalled_exercise(user_id),
            self._insight_streak_milestone(user_id),
            self._insight_volume_trend(user_id),
            self._insight_recovery(user_id),
            self._insight_overdue_skill(user_id),
            self._insight_habit_fitness_correlation(user_id),
            return_exceptions=True,
        )

        cards: list[InsightCard] = []
        for r in results:
            if isinstance(r, InsightCard):
                cards.append(r)
            elif isinstance(r, list):
                cards.extend(r)
        return cards[:3]

    async def _insight_stalled_exercise(self, user_id: UUID) -> list[InsightCard]:
        """Max weight unchanged for 3+ sessions → suggest deload."""
        result = await self.db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
            )
            .options(
                selectinload(WorkoutSession.sets).selectinload(WorkoutSet.exercise)
            )
            .order_by(WorkoutSession.started_at.desc())
            .limit(20)
        )
        sessions = list(result.scalars().all())

        # Group sets by exercise across sessions
        exercise_maxes: dict[UUID, list[float]] = defaultdict(list)
        exercise_names: dict[UUID, str] = {}
        for session in sessions:
            session_ex: dict[UUID, float] = {}
            for ws in session.sets:
                if ws.completed and ws.weight_kg > 0:
                    exercise_names[ws.exercise_id] = ws.exercise.name
                    session_ex[ws.exercise_id] = max(
                        session_ex.get(ws.exercise_id, 0), ws.weight_kg
                    )
            for ex_id, max_w in session_ex.items():
                exercise_maxes[ex_id].append(max_w)

        cards = []
        for ex_id, maxes in exercise_maxes.items():
            if len(maxes) >= 3 and len(set(maxes[:3])) == 1:
                name = exercise_names.get(ex_id, "Exercise")
                cards.append(
                    InsightCard(
                        id=f"stalled-{ex_id}",
                        icon="trending-down",
                        domain="fitness",
                        color="#3B82F6",
                        title=f"{name} plateau",
                        message="Same max weight for 3 sessions. Consider a deload week or vary rep ranges.",
                    )
                )
        return cards[:1]

    async def _insight_streak_milestone(self, user_id: UUID) -> list[InsightCard]:
        """Any habit hitting 7/14/30/60/100 days → celebrate."""
        streaks_resp = await self.get_all_streaks(user_id)
        milestones = [7, 14, 30, 60, 100]

        cards = []
        for s in streaks_resp.streaks:
            if s.domain == "habits" and s.current_streak in milestones:
                cards.append(
                    InsightCard(
                        id=f"milestone-{s.entity_id}",
                        icon="trophy",
                        domain="habits",
                        color="#22c55e",
                        title=f"{s.current_streak}-day streak!",
                        message=f"'{s.name}' has hit {s.current_streak} consecutive days. Keep it going!",
                    )
                )
        return cards[:1]

    async def _insight_volume_trend(self, user_id: UUID) -> InsightCard | list:
        """Weekly volume up/down 20%+ over last 4 weeks."""
        trends = await self._fitness_trends(user_id, 35)
        vol_series = next((s for s in trends if s.metric == "volume"), None)
        if not vol_series or len(vol_series.data) < 4:
            return []

        recent = vol_series.data[-2:]
        earlier = vol_series.data[-4:-2]
        avg_recent = sum(p.value for p in recent) / len(recent) if recent else 0
        avg_earlier = sum(p.value for p in earlier) / len(earlier) if earlier else 0

        if avg_earlier == 0:
            return []

        change = (avg_recent - avg_earlier) / avg_earlier * 100
        if abs(change) >= 20:
            direction = "up" if change > 0 else "down"
            icon = "trending-up" if change > 0 else "trending-down"
            return InsightCard(
                id="volume-trend",
                icon=icon,
                domain="fitness",
                color="#3B82F6",
                title=f"Volume {direction} {abs(change):.0f}%",
                message=f"Your training volume is trending {direction} over the last 4 weeks.",
            )
        return []

    async def _insight_recovery(self, user_id: UUID) -> InsightCard | list:
        """4+ workouts this week → suggest rest day."""
        today = date.today()
        week_start = datetime.combine(
            today - timedelta(days=today.weekday()),
            datetime.min.time(),
            tzinfo=timezone.utc,
        )
        result = await self.db.execute(
            select(func.count())
            .select_from(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
                WorkoutSession.started_at >= week_start,
            )
        )
        count = result.scalar() or 0
        if count >= 4:
            return InsightCard(
                id="recovery",
                icon="battery-low",
                domain="fitness",
                color="#F59E0B",
                title="Recovery check",
                message=f"{count} workouts this week. Consider scheduling a rest day for recovery.",
            )
        return []

    async def _insight_overdue_skill(self, user_id: UUID) -> list[InsightCard]:
        """Skill not practiced in 7+ days with due sub-skills."""
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        skills_result = await self.db.execute(
            select(SkillDefinition)
            .where(
                SkillDefinition.user_id == user_id,
                SkillDefinition.is_active == True,  # noqa: E712
            )
            .options(selectinload(SkillDefinition.competency_levels))
        )
        skills = list(skills_result.scalars().all())

        cards = []
        for skill in skills:
            # Check for due sub-skills
            due_count = sum(
                1
                for cl in skill.competency_levels
                if cl.next_review_date
                and cl.next_review_date <= datetime.now(timezone.utc)
            )
            if due_count == 0:
                continue

            # Check last practice
            last_result = await self.db.execute(
                select(PracticeSession.practiced_at)
                .where(PracticeSession.skill_id == skill.id)
                .order_by(PracticeSession.practiced_at.desc())
                .limit(1)
            )
            last_row = last_result.first()
            if last_row and last_row[0] < seven_days_ago:
                cards.append(
                    InsightCard(
                        id=f"overdue-{skill.id}",
                        icon="alert-circle",
                        domain="skills",
                        color="#8B5CF6",
                        title=f"Practice '{skill.name}'",
                        message=f"{due_count} sub-skill{'s' if due_count > 1 else ''} due for review. Last practiced 7+ days ago.",
                    )
                )
        return cards[:1]

    async def _insight_habit_fitness_correlation(
        self, user_id: UUID
    ) -> InsightCard | list:
        """If habits.completion_rate correlates (r > 0.5) with fitness.volume."""
        try:
            corr = await self.get_correlations(
                user_id, "habits.completion_rate", "fitness.volume", 90
            )
            if corr.correlation_coefficient and corr.correlation_coefficient > 0.5:
                return InsightCard(
                    id="habit-fitness-corr",
                    icon="link",
                    domain="habits",
                    color="#22c55e",
                    title="Habits boost workouts",
                    message=f"Your habit consistency correlates with training volume (r={corr.correlation_coefficient:.2f}).",
                )
        except Exception:
            pass
        return []

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.fitness.models import (
    Exercise,
    TemplateExercise,
    WorkoutSession,
    WorkoutSet,
    WorkoutTemplate,
)
from src.modules.fitness.schemas import (
    ExerciseCreate,
    StartSessionRequest,
    WorkoutSetCreate,
    WorkoutTemplateCreate,
    WorkoutTemplateUpdate,
)


class FitnessService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Exercises ---

    async def list_exercises(
        self, user_id: UUID, category: str | None = None, muscle_group: str | None = None
    ) -> list[Exercise]:
        query = select(Exercise).where(
            (Exercise.user_id == None) | (Exercise.user_id == user_id)  # noqa: E711
        )
        if category:
            query = query.where(Exercise.category == category)
        if muscle_group:
            query = query.where(
                Exercise.muscle_groups.op("@>")(f'["{muscle_group}"]')
            )
        query = query.order_by(Exercise.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_exercise(self, user_id: UUID, data: ExerciseCreate) -> Exercise:
        exercise = Exercise(
            user_id=user_id,
            name=data.name,
            category=data.category,
            muscle_groups=data.muscle_groups,
            equipment=data.equipment,
            is_custom=True,
        )
        self.db.add(exercise)
        await self.db.flush()
        await self.db.refresh(exercise)
        return exercise

    async def get_exercise(self, exercise_id: UUID) -> Exercise | None:
        result = await self.db.execute(
            select(Exercise).where(Exercise.id == exercise_id)
        )
        return result.scalar_one_or_none()

    # --- Templates ---

    async def list_templates(self, user_id: UUID) -> list[WorkoutTemplate]:
        result = await self.db.execute(
            select(WorkoutTemplate)
            .where(WorkoutTemplate.user_id == user_id)
            .options(
                selectinload(WorkoutTemplate.exercises).selectinload(TemplateExercise.exercise)
            )
            .order_by(WorkoutTemplate.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_template(self, user_id: UUID, template_id: UUID) -> WorkoutTemplate | None:
        result = await self.db.execute(
            select(WorkoutTemplate)
            .where(WorkoutTemplate.id == template_id, WorkoutTemplate.user_id == user_id)
            .options(
                selectinload(WorkoutTemplate.exercises).selectinload(TemplateExercise.exercise)
            )
        )
        return result.scalar_one_or_none()

    async def create_template(self, user_id: UUID, data: WorkoutTemplateCreate) -> WorkoutTemplate:
        template = WorkoutTemplate(
            user_id=user_id,
            name=data.name,
            description=data.description,
        )
        self.db.add(template)
        await self.db.flush()

        for ex_data in data.exercises:
            te = TemplateExercise(
                template_id=template.id,
                exercise_id=ex_data.exercise_id,
                sort_order=ex_data.sort_order,
                target_sets=ex_data.target_sets,
                target_reps=ex_data.target_reps,
                target_weight_kg=ex_data.target_weight_kg,
                set_type=ex_data.set_type,
                rest_seconds=ex_data.rest_seconds,
            )
            self.db.add(te)

        await self.db.flush()

        # Reload with relationships
        return await self.get_template(user_id, template.id)  # type: ignore

    async def update_template(
        self, user_id: UUID, template_id: UUID, data: WorkoutTemplateUpdate
    ) -> WorkoutTemplate | None:
        template = await self.get_template(user_id, template_id)
        if not template:
            return None

        if data.name is not None:
            template.name = data.name
        if data.description is not None:
            template.description = data.description

        if data.exercises is not None:
            # Replace all exercises
            await self.db.execute(
                delete(TemplateExercise).where(TemplateExercise.template_id == template_id)
            )
            for ex_data in data.exercises:
                te = TemplateExercise(
                    template_id=template_id,
                    exercise_id=ex_data.exercise_id,
                    sort_order=ex_data.sort_order,
                    target_sets=ex_data.target_sets,
                    target_reps=ex_data.target_reps,
                    target_weight_kg=ex_data.target_weight_kg,
                    set_type=ex_data.set_type,
                    rest_seconds=ex_data.rest_seconds,
                )
                self.db.add(te)

        await self.db.flush()
        return await self.get_template(user_id, template_id)

    async def delete_template(self, user_id: UUID, template_id: UUID) -> bool:
        template = await self.get_template(user_id, template_id)
        if not template:
            return False
        await self.db.delete(template)
        await self.db.flush()
        return True

    # --- Sessions ---

    async def start_session(self, user_id: UUID, data: StartSessionRequest) -> WorkoutSession:
        session = WorkoutSession(
            user_id=user_id,
            template_id=data.template_id,
            status="in_progress",
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_active_session(self, user_id: UUID) -> WorkoutSession | None:
        result = await self.db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "in_progress",
            )
            .options(
                selectinload(WorkoutSession.sets).selectinload(WorkoutSet.exercise),
                selectinload(WorkoutSession.template),
            )
            .order_by(WorkoutSession.started_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_session(self, user_id: UUID, session_id: UUID) -> WorkoutSession | None:
        result = await self.db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.id == session_id, WorkoutSession.user_id == user_id)
            .options(
                selectinload(WorkoutSession.sets).selectinload(WorkoutSet.exercise),
                selectinload(WorkoutSession.template),
            )
        )
        return result.scalar_one_or_none()

    async def log_set(self, user_id: UUID, session_id: UUID, data: WorkoutSetCreate) -> WorkoutSet:
        session = await self.get_session(user_id, session_id)
        if not session:
            raise ValueError("Session not found")
        if session.status != "in_progress":
            raise ValueError("Session is not in progress")

        workout_set = WorkoutSet(
            session_id=session_id,
            exercise_id=data.exercise_id,
            set_number=data.set_number,
            weight_kg=data.weight_kg,
            reps=data.reps,
            rpe=data.rpe,
            set_type=data.set_type,
            completed=data.completed,
        )
        self.db.add(workout_set)
        await self.db.flush()
        await self.db.refresh(workout_set)
        return workout_set

    async def delete_set(self, user_id: UUID, session_id: UUID, set_id: UUID) -> bool:
        session = await self.get_session(user_id, session_id)
        if not session:
            return False
        if session.status != "in_progress":
            return False

        result = await self.db.execute(
            delete(WorkoutSet)
            .where(WorkoutSet.id == set_id, WorkoutSet.session_id == session_id)
            .returning(WorkoutSet.id)
        )
        return len(result.all()) > 0

    async def complete_session(
        self, user_id: UUID, session_id: UUID, notes: str | None = None
    ) -> WorkoutSession | None:
        session = await self.get_session(user_id, session_id)
        if not session:
            return None
        if session.status != "in_progress":
            return None

        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        if notes:
            session.notes = notes
        await self.db.flush()
        return await self.get_session(user_id, session_id)

    async def list_sessions(
        self, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[WorkoutSession]:
        result = await self.db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id)
            .options(
                selectinload(WorkoutSession.sets).selectinload(WorkoutSet.exercise),
                selectinload(WorkoutSession.template),
            )
            .order_by(WorkoutSession.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    # --- Stats ---

    async def get_exercise_history(
        self, user_id: UUID, exercise_id: UUID, limit: int = 10
    ) -> list[dict]:
        """Get the last N sessions that include this exercise."""
        result = await self.db.execute(
            select(WorkoutSet)
            .join(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSet.exercise_id == exercise_id,
                WorkoutSession.status == "completed",
                WorkoutSet.completed == True,  # noqa: E712
            )
            .order_by(WorkoutSet.logged_at.desc())
        )
        sets = list(result.scalars().all())

        # Group by session
        sessions: dict[UUID, list] = {}
        for s in sets:
            sessions.setdefault(s.session_id, []).append(s)

        # Return most recent N sessions
        session_list = list(sessions.items())[:limit]
        return [
            {
                "session_id": sid,
                "sets": [
                    {
                        "set_number": ws.set_number,
                        "weight_kg": ws.weight_kg,
                        "reps": ws.reps,
                        "rpe": ws.rpe,
                        "set_type": ws.set_type,
                        "logged_at": ws.logged_at,
                    }
                    for ws in session_sets
                ],
            }
            for sid, session_sets in session_list
        ]

    async def get_exercise_progression(
        self, user_id: UUID, exercise_id: UUID,
        from_date: date | None = None, to_date: date | None = None,
    ) -> list[dict]:
        """Time-series: date, max_weight, best_set, volume per session."""
        query = (
            select(WorkoutSet, WorkoutSession.started_at)
            .join(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSet.exercise_id == exercise_id,
                WorkoutSession.status == "completed",
                WorkoutSet.completed == True,  # noqa: E712
            )
        )
        if from_date:
            query = query.where(WorkoutSession.started_at >= datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc))
        if to_date:
            query = query.where(WorkoutSession.started_at <= datetime.combine(to_date, datetime.max.time(), tzinfo=timezone.utc))
        query = query.order_by(WorkoutSession.started_at)
        result = await self.db.execute(query)
        rows = result.all()

        # Group by session date
        sessions: dict[datetime, list] = {}
        for ws, started_at in rows:
            sessions.setdefault(started_at, []).append(ws)

        progression = []
        for started_at, session_sets in sessions.items():
            max_weight = max(s.weight_kg for s in session_sets)
            best_set = max(session_sets, key=lambda s: s.weight_kg)
            volume = sum(s.weight_kg * s.reps for s in session_sets)
            progression.append({
                "date": started_at,
                "max_weight": max_weight,
                "best_set_weight": best_set.weight_kg,
                "best_set_reps": best_set.reps,
                "volume": volume,
                "sets_count": len(session_sets),
            })

        return progression

    async def get_overview_stats(
        self, user_id: UUID, from_date: date | None = None, to_date: date | None = None,
    ) -> dict:
        """Aggregate stats for the analytics dashboard."""
        # Default range: last 12 weeks
        if not to_date:
            to_date = date.today()
        if not from_date:
            from_date = to_date - timedelta(weeks=12)

        from_dt = datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc)
        to_dt = datetime.combine(to_date, datetime.max.time(), tzinfo=timezone.utc)

        # Fetch all completed sessions with sets in date range
        result = await self.db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
                WorkoutSession.started_at >= from_dt,
                WorkoutSession.started_at <= to_dt,
            )
            .options(
                selectinload(WorkoutSession.sets).selectinload(WorkoutSet.exercise),
            )
            .order_by(WorkoutSession.started_at)
        )
        sessions = list(result.scalars().all())

        # Weekly volume + session count
        weekly: dict[str, dict] = {}
        # Generate all weeks in range so empty weeks show as zero
        current = from_date - timedelta(days=from_date.weekday())  # Monday
        end = to_date
        while current <= end:
            key = current.isoformat()
            weekly[key] = {"week_start": key, "total_volume": 0.0, "session_count": 0}
            current += timedelta(weeks=1)

        # Muscle group volume
        muscle_groups: dict[str, float] = {}

        total_volume = 0.0
        for session in sessions:
            session_date = session.started_at.date() if isinstance(session.started_at, datetime) else session.started_at
            week_start = session_date - timedelta(days=session_date.weekday())
            wk = week_start.isoformat()
            if wk not in weekly:
                weekly[wk] = {"week_start": wk, "total_volume": 0.0, "session_count": 0}
            weekly[wk]["session_count"] += 1

            for ws in session.sets:
                if ws.completed:
                    vol = ws.weight_kg * ws.reps
                    total_volume += vol
                    weekly[wk]["total_volume"] += vol
                    # Accumulate muscle group volume
                    for mg in (ws.exercise.muscle_groups or []):
                        muscle_groups[mg] = muscle_groups.get(mg, 0.0) + vol

        # Current streak: consecutive weeks (ending this week) with at least 1 workout
        sorted_weeks = sorted(weekly.values(), key=lambda w: w["week_start"], reverse=True)
        current_streak = 0
        for w in sorted_weeks:
            if w["session_count"] > 0:
                current_streak += 1
            else:
                break

        weekly_volume = sorted(weekly.values(), key=lambda w: w["week_start"])
        muscle_group_volume = sorted(
            [{"muscle_group": mg, "volume": round(vol, 1)} for mg, vol in muscle_groups.items()],
            key=lambda x: x["volume"],
            reverse=True,
        )

        return {
            "weekly_volume": weekly_volume,
            "muscle_group_volume": muscle_group_volume,
            "total_workouts": len(sessions),
            "total_volume": round(total_volume, 1),
            "current_streak": current_streak,
        }

    async def get_trained_exercises(self, user_id: UUID) -> list[Exercise]:
        """Get unique exercises the user has logged in completed sessions."""
        result = await self.db.execute(
            select(Exercise)
            .join(WorkoutSet, WorkoutSet.exercise_id == Exercise.id)
            .join(WorkoutSession, WorkoutSession.id == WorkoutSet.session_id)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
                WorkoutSet.completed == True,  # noqa: E712
            )
            .distinct()
            .order_by(Exercise.name)
        )
        return list(result.scalars().all())

    async def get_previous_performance(
        self, user_id: UUID, exercise_id: UUID
    ) -> list[dict] | None:
        """Get sets from the most recent completed session for this exercise."""
        # Find the most recent completed session containing this exercise
        result = await self.db.execute(
            select(WorkoutSet)
            .join(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSet.exercise_id == exercise_id,
                WorkoutSession.status == "completed",
                WorkoutSet.completed == True,  # noqa: E712
            )
            .order_by(WorkoutSession.started_at.desc())
        )
        all_sets = list(result.scalars().all())
        if not all_sets:
            return None

        # Get the most recent session_id
        latest_session_id = all_sets[0].session_id
        return [
            {
                "set_number": s.set_number,
                "weight_kg": s.weight_kg,
                "reps": s.reps,
            }
            for s in all_sets
            if s.session_id == latest_session_id
        ]

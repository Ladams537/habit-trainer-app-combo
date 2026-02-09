import csv
import io
from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.fitness.models import WorkoutSession, WorkoutSet
from src.modules.habits.models import HabitCompletion, HabitDefinition
from src.modules.skills.models import PracticeSession, SkillDefinition


class ExportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_workouts(self, user_id: UUID) -> AsyncGenerator[str, None]:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "date",
                "exercise",
                "set_number",
                "reps",
                "weight_kg",
                "volume",
                "rpe",
                "set_type",
            ]
        )
        yield buf.getvalue()
        buf.seek(0)
        buf.truncate(0)

        result = await self.db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id, WorkoutSession.status == "completed"
            )
            .options(
                selectinload(WorkoutSession.sets).selectinload(WorkoutSet.exercise)
            )
            .order_by(WorkoutSession.started_at.desc())
        )
        sessions = result.scalars().all()

        for session in sessions:
            date_str = session.started_at.strftime("%Y-%m-%d")
            for s in session.sets:
                volume = s.weight_kg * s.reps
                writer.writerow(
                    [
                        date_str,
                        s.exercise.name,
                        s.set_number,
                        s.reps,
                        s.weight_kg,
                        round(volume, 1),
                        s.rpe or "",
                        s.set_type,
                    ]
                )
                yield buf.getvalue()
                buf.seek(0)
                buf.truncate(0)

    async def export_habits(self, user_id: UUID) -> AsyncGenerator[str, None]:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["habit_name", "date", "value", "completed"])
        yield buf.getvalue()
        buf.seek(0)
        buf.truncate(0)

        result = await self.db.execute(
            select(HabitCompletion)
            .join(HabitDefinition)
            .where(HabitDefinition.user_id == user_id)
            .options(selectinload(HabitCompletion.habit))
            .order_by(HabitCompletion.completed_at.desc())
        )
        completions = result.scalars().all()

        for c in completions:
            writer.writerow(
                [
                    c.habit.name,
                    c.completed_at.strftime("%Y-%m-%d"),
                    float(c.value),
                    c.completed,
                ]
            )
            yield buf.getvalue()
            buf.seek(0)
            buf.truncate(0)

    async def export_skills(self, user_id: UUID) -> AsyncGenerator[str, None]:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            ["skill_name", "date", "duration_minutes", "quality_rating", "focus_area"]
        )
        yield buf.getvalue()
        buf.seek(0)
        buf.truncate(0)

        result = await self.db.execute(
            select(PracticeSession)
            .join(SkillDefinition)
            .where(SkillDefinition.user_id == user_id)
            .options(selectinload(PracticeSession.skill))
            .order_by(PracticeSession.practiced_at.desc())
        )
        sessions = result.scalars().all()

        for s in sessions:
            writer.writerow(
                [
                    s.skill.name,
                    s.practiced_at.strftime("%Y-%m-%d"),
                    s.duration_minutes,
                    s.quality_rating,
                    s.focus_area or "",
                ]
            )
            yield buf.getvalue()
            buf.seek(0)
            buf.truncate(0)

    async def export_all_json(self, user_id: UUID) -> dict:
        # Habits
        habits_result = await self.db.execute(
            select(HabitDefinition)
            .where(HabitDefinition.user_id == user_id)
            .options(selectinload(HabitDefinition.completions))
        )
        habits = habits_result.scalars().all()

        habits_data = []
        for h in habits:
            habits_data.append(
                {
                    "name": h.name,
                    "type": h.habit_type,
                    "frequency": h.frequency,
                    "target_value": float(h.target_value),
                    "unit": h.unit,
                    "color": h.color,
                    "completions": [
                        {
                            "date": c.completed_at.isoformat(),
                            "value": float(c.value),
                            "completed": c.completed,
                        }
                        for c in h.completions
                    ],
                }
            )

        # Workouts
        sessions_result = await self.db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id)
            .options(
                selectinload(WorkoutSession.sets).selectinload(WorkoutSet.exercise)
            )
            .order_by(WorkoutSession.started_at.desc())
        )
        sessions = sessions_result.scalars().all()

        workouts_data = []
        for sess in sessions:
            workouts_data.append(
                {
                    "date": sess.started_at.isoformat(),
                    "completed_at": sess.completed_at.isoformat()
                    if sess.completed_at
                    else None,
                    "status": sess.status,
                    "notes": sess.notes,
                    "sets": [
                        {
                            "exercise": s.exercise.name,
                            "set_number": s.set_number,
                            "reps": s.reps,
                            "weight_kg": s.weight_kg,
                            "rpe": s.rpe,
                            "set_type": s.set_type,
                        }
                        for s in sess.sets
                    ],
                }
            )

        # Skills
        skills_result = await self.db.execute(
            select(SkillDefinition)
            .where(SkillDefinition.user_id == user_id)
            .options(selectinload(SkillDefinition.practice_sessions))
        )
        skills = skills_result.scalars().all()

        skills_data = []
        for sk in skills:
            skills_data.append(
                {
                    "name": sk.name,
                    "category": sk.category,
                    "current_level": sk.current_level,
                    "total_practice_minutes": sk.total_practice_minutes,
                    "practice_sessions": [
                        {
                            "date": ps.practiced_at.isoformat(),
                            "duration_minutes": ps.duration_minutes,
                            "quality_rating": ps.quality_rating,
                            "focus_area": ps.focus_area,
                            "notes": ps.notes,
                        }
                        for ps in sk.practice_sessions
                    ],
                }
            )

        return {
            "habits": habits_data,
            "workouts": workouts_data,
            "skills": skills_data,
        }

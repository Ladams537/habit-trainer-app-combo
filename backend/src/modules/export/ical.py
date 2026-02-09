from datetime import timedelta
from uuid import UUID

from icalendar import Calendar, Event
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.fitness.models import WorkoutSession, WorkoutSet
from src.modules.habits.models import HabitDefinition
from src.modules.skills.models import CompetencyLevel, SkillDefinition


async def generate_ical_feed(db: AsyncSession, user_id: UUID) -> str:
    cal = Calendar()
    cal.add("prodid", "-//Trainer App//EN")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", "Trainer")

    # Recent completed workouts as events
    sessions_result = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id, WorkoutSession.status == "completed")
        .options(selectinload(WorkoutSession.sets).selectinload(WorkoutSet.exercise))
        .order_by(WorkoutSession.started_at.desc())
        .limit(100)
    )
    sessions = sessions_result.scalars().all()

    for sess in sessions:
        event = Event()
        exercises = {s.exercise.name for s in sess.sets}
        event.add("summary", f"Workout: {', '.join(sorted(exercises)[:3])}")
        event.add("dtstart", sess.started_at)
        event.add("dtend", sess.completed_at or (sess.started_at + timedelta(hours=1)))
        event.add("uid", f"workout-{sess.id}@trainer")

        total_volume = sum(s.weight_kg * s.reps for s in sess.sets)
        desc = f"Sets: {len(sess.sets)} | Volume: {total_volume:.0f}kg"
        if sess.notes:
            desc += f"\n{sess.notes}"
        event.add("description", desc)
        cal.add_component(event)

    # Habit schedules as recurring daily events
    habits_result = await db.execute(
        select(HabitDefinition).where(
            HabitDefinition.user_id == user_id, HabitDefinition.is_active.is_(True)
        )
    )
    habits = habits_result.scalars().all()

    for habit in habits:
        event = Event()
        event.add("summary", f"Habit: {habit.name}")
        event.add("dtstart", habit.created_at.date())
        event.add("uid", f"habit-{habit.id}@trainer")
        if habit.frequency == "daily":
            event.add("rrule", {"freq": "daily"})
        elif habit.frequency == "weekly":
            event.add("rrule", {"freq": "weekly"})
        cal.add_component(event)

    # Sub-skills due for review
    comps_result = await db.execute(
        select(CompetencyLevel)
        .join(SkillDefinition)
        .where(
            SkillDefinition.user_id == user_id,
            CompetencyLevel.next_review_date.isnot(None),
        )
        .options(selectinload(CompetencyLevel.skill))
    )
    competencies = comps_result.scalars().all()

    for comp in competencies:
        if comp.next_review_date:
            event = Event()
            event.add("summary", f"Review: {comp.skill.name} - {comp.sub_skill}")
            event.add("dtstart", comp.next_review_date.date())
            event.add("uid", f"review-{comp.id}@trainer")
            cal.add_component(event)

    return cal.to_ical().decode("utf-8")

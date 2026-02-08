"""
Seed realistic test data for the Personal Trainer Application.

Generates ~50 completed workout sessions over 14 weeks with progressive overload,
a deload week, and realistic variance. Creates 3 PPL workout templates.

Run from backend directory:
    .venv/bin/python -m scripts.seed_test_data
"""

import argparse
import asyncio
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from src.modules.auth.models import User
from src.modules.fitness.models import (
    Exercise,
    TemplateExercise,
    WorkoutSession,
    WorkoutSet,
    WorkoutTemplate,
)
from src.modules.fitness.seed_exercises import seed_built_in_exercises
from src.shared.auth import hash_password
from src.shared.database import async_session

# --- Template definitions ---

TEMPLATES = {
    "Push": [
        "Barbell Bench Press",
        "Incline Dumbbell Press",
        "Overhead Press",
        "Lateral Raise",
        "Tricep Pushdown",
        "Cable Fly",
    ],
    "Pull": [
        "Deadlift",
        "Barbell Row",
        "Pull Up",
        "Lat Pulldown",
        "Barbell Curl",
        "Face Pull",
    ],
    "Legs": [
        "Barbell Squat",
        "Romanian Deadlift",
        "Leg Press",
        "Leg Curl",
        "Leg Extension",
        "Calf Raise",
    ],
}

# Exercise progression config: (start_weight, weekly_increment, base_reps, base_sets)
EXERCISE_CONFIG = {
    "Barbell Bench Press": (60.0, 1.25, 8, 4),
    "Incline Dumbbell Press": (20.0, 0.5, 10, 3),
    "Overhead Press": (35.0, 1.25, 8, 4),
    "Lateral Raise": (10.0, 0.5, 12, 3),
    "Tricep Pushdown": (15.0, 0.5, 12, 3),
    "Cable Fly": (12.5, 0.5, 12, 3),
    "Deadlift": (100.0, 2.5, 5, 4),
    "Barbell Row": (60.0, 1.25, 8, 4),
    "Pull Up": (0.0, 0.0, 8, 3),  # bodyweight — reps progress instead
    "Lat Pulldown": (50.0, 1.0, 10, 3),
    "Barbell Curl": (25.0, 0.5, 10, 3),
    "Face Pull": (12.5, 0.5, 15, 3),
    "Barbell Squat": (80.0, 2.5, 6, 4),
    "Romanian Deadlift": (70.0, 1.25, 8, 3),
    "Leg Press": (120.0, 2.5, 10, 4),
    "Leg Curl": (30.0, 1.0, 12, 3),
    "Leg Extension": (30.0, 1.0, 12, 3),
    "Calf Raise": (40.0, 1.0, 15, 4),
}

DELOAD_WEEK = 7  # 0-indexed, so week 8 in human terms


def round_to_nearest(value: float, step: float) -> float:
    """Round weight to nearest plate increment."""
    if step == 0:
        return value
    return round(value / step) * step


def generate_session_schedule(num_weeks: int = 14) -> list[tuple[int, int, str]]:
    """Generate a realistic training schedule: (week, day_offset, template_name).

    Returns ~3-5 sessions per week cycling Push/Pull/Legs with rest days.
    """
    schedule = []
    template_cycle = ["Push", "Pull", "Legs"]
    cycle_idx = 0

    for week in range(num_weeks):
        # Decide sessions this week: mostly 4, sometimes 3 or 5
        r = random.random()
        if r < 0.15:
            sessions_this_week = 3
        elif r < 0.75:
            sessions_this_week = 4
        else:
            sessions_this_week = 5

        # Deload week: fewer sessions
        if week == DELOAD_WEEK:
            sessions_this_week = 3

        # Pick which days to train (0=Mon..6=Sun), ensuring rest days
        available_days = list(range(7))
        training_days = sorted(random.sample(available_days, sessions_this_week))

        for day in training_days:
            template_name = template_cycle[cycle_idx % 3]
            schedule.append((week, day, template_name))
            cycle_idx += 1

    return schedule


def generate_sets_for_exercise(
    exercise_name: str,
    week: int,
    is_deload: bool,
) -> list[dict]:
    """Generate realistic sets for an exercise at a given week of progression."""
    start_weight, weekly_inc, base_reps, base_sets = EXERCISE_CONFIG[exercise_name]

    # Progressive weight
    current_weight = start_weight + (weekly_inc * week)

    # Deload: ~60% weight, fewer sets
    if is_deload:
        current_weight *= 0.6
        num_sets = max(2, base_sets - 1)
        base_reps = base_reps  # keep reps the same on deload
    else:
        num_sets = base_sets

    # Round to nearest 1.25 for barbells, 0.5 for cables/dumbbells
    if start_weight >= 25:
        current_weight = round_to_nearest(current_weight, 2.5)
    else:
        current_weight = round_to_nearest(current_weight, 0.5)

    sets = []
    for set_num in range(1, num_sets + 1):
        # Weight variance: ±5%
        noise = random.uniform(-0.05, 0.05)
        set_weight = max(0, current_weight * (1 + noise))

        # Round weight
        if start_weight >= 25:
            set_weight = round_to_nearest(set_weight, 2.5)
        elif start_weight > 0:
            set_weight = round_to_nearest(set_weight, 0.5)
        else:
            set_weight = 0.0  # bodyweight

        # Rep variance: reps decrease slightly on later sets
        fatigue_drop = 0
        if set_num == base_sets and not is_deload:
            fatigue_drop = random.choice([0, 1, 2])
        elif set_num == base_sets - 1 and not is_deload:
            fatigue_drop = random.choice([0, 0, 1])

        actual_reps = base_reps - fatigue_drop + random.randint(-1, 1)
        actual_reps = max(3, actual_reps)

        # Pull-ups: bodyweight reps increase over time instead of weight
        if exercise_name == "Pull Up":
            actual_reps = base_reps + (week // 3) + random.randint(-1, 1)
            actual_reps = max(3, actual_reps)

        # RPE: earlier sets lower RPE, later sets harder
        base_rpe = 7 if is_deload else 8
        rpe = min(10, base_rpe + (set_num - 1) + random.choice([-1, 0, 0, 0, 1]))

        # Occasional failed set on last set of heavy compounds
        set_type = "working"
        if (
            not is_deload
            and set_num == num_sets
            and start_weight >= 50
            and random.random() < 0.08
        ):
            set_type = "failure"
            actual_reps = max(2, actual_reps - 2)
            rpe = 10

        sets.append({
            "set_number": set_num,
            "weight_kg": set_weight,
            "reps": actual_reps,
            "rpe": rpe,
            "set_type": set_type,
            "completed": True,
        })

    return sets


async def seed(target_email: str | None = None, target_password: str | None = None):
    async with async_session() as session:
        # 1. Ensure built-in exercises exist
        inserted = await seed_built_in_exercises(session)
        if inserted:
            print(f"Seeded {inserted} built-in exercises")
        await session.commit()

    async with async_session() as session:
        # 2. Get or create user
        if target_email:
            result = await session.execute(
                select(User).where(User.email == target_email)
            )
            user = result.scalar_one_or_none()
            if user is None:
                password = target_password or "password123"
                user = User(
                    email=target_email,
                    password_hash=hash_password(password),
                    display_name=target_email.split("@")[0].title(),
                )
                session.add(user)
                await session.flush()
                print(f"Created user: {user.email}")
            else:
                print(f"Using existing user: {user.email}")
        else:
            result = await session.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            if user is None:
                user = User(
                    email="test@trainer.app",
                    password_hash=hash_password("password123"),
                    display_name="Test User",
                )
                session.add(user)
                await session.flush()
                print(f"Created test user: {user.email}")
            else:
                print(f"Using existing user: {user.email}")

        user_id = user.id

        # 3. Lookup exercise UUIDs
        result = await session.execute(
            select(Exercise).where(Exercise.user_id.is_(None))
        )
        all_exercises = {ex.name: ex for ex in result.scalars().all()}

        # Verify all needed exercises exist
        needed = set()
        for exercises in TEMPLATES.values():
            needed.update(exercises)

        missing = needed - set(all_exercises.keys())
        if missing:
            print(f"ERROR: Missing exercises: {missing}")
            print("Run seed_built_in_exercises first.")
            return

        # 4. Create workout templates
        templates = {}
        for template_name, exercise_names in TEMPLATES.items():
            template = WorkoutTemplate(
                user_id=user_id,
                name=template_name,
                description=f"{template_name} day — PPL split",
            )
            session.add(template)
            await session.flush()

            for i, ex_name in enumerate(exercise_names):
                config = EXERCISE_CONFIG[ex_name]
                te = TemplateExercise(
                    template_id=template.id,
                    exercise_id=all_exercises[ex_name].id,
                    sort_order=i,
                    target_sets=config[3],
                    target_reps=config[2],
                    target_weight_kg=config[0],
                )
                session.add(te)

            templates[template_name] = template

        await session.flush()
        print(f"Created {len(templates)} templates: {', '.join(templates.keys())}")

        # 5. Generate sessions
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(weeks=14)
        schedule = generate_session_schedule(14)

        total_sessions = 0
        total_sets = 0

        for week, day_offset, template_name in schedule:
            is_deload = week == DELOAD_WEEK

            # Calculate session datetime
            session_date = start_date + timedelta(weeks=week, days=day_offset)
            # Random start time between 6am-7pm
            hour = random.randint(6, 19)
            minute = random.choice([0, 15, 30, 45])
            started_at = session_date.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )

            # Session duration: 45-75 min (deload shorter)
            if is_deload:
                duration_min = random.randint(35, 50)
            else:
                duration_min = random.randint(45, 75)
            completed_at = started_at + timedelta(minutes=duration_min)

            workout_session = WorkoutSession(
                user_id=user_id,
                template_id=templates[template_name].id,
                started_at=started_at,
                completed_at=completed_at,
                status="completed",
                notes=None,
            )
            session.add(workout_session)
            await session.flush()

            # Generate sets for each exercise in the template
            exercise_names = TEMPLATES[template_name]
            for ex_name in exercise_names:
                exercise = all_exercises[ex_name]
                sets_data = generate_sets_for_exercise(ex_name, week, is_deload)

                for s in sets_data:
                    # Stagger logged_at times throughout the session
                    set_offset = timedelta(
                        minutes=random.randint(0, duration_min - 1),
                        seconds=random.randint(0, 59),
                    )
                    workout_set = WorkoutSet(
                        session_id=workout_session.id,
                        exercise_id=exercise.id,
                        set_number=s["set_number"],
                        weight_kg=s["weight_kg"],
                        reps=s["reps"],
                        rpe=s["rpe"],
                        set_type=s["set_type"],
                        completed=s["completed"],
                        logged_at=started_at + set_offset,
                    )
                    session.add(workout_set)
                    total_sets += 1

            total_sessions += 1

        await session.commit()
        print(f"\nSeed complete!")
        print(f"  Created {len(templates)} templates")
        print(f"  Created {total_sessions} sessions over 14 weeks")
        print(f"  Created {total_sets} sets")
        print(f"  Deload week: week {DELOAD_WEEK + 1}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed test workout data")
    parser.add_argument("--email", help="Target user email (creates user if not found)")
    parser.add_argument("--password", help="Password for new user (only used if creating)")
    args = parser.parse_args()
    asyncio.run(seed(target_email=args.email, target_password=args.password))

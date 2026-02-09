from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.fitness.models import Exercise

BUILT_IN_EXERCISES = [
    # --- Chest ---
    {
        "name": "Barbell Bench Press",
        "category": "compound",
        "muscle_groups": ["chest", "triceps", "shoulders"],
        "equipment": "barbell",
    },
    {
        "name": "Incline Barbell Bench Press",
        "category": "compound",
        "muscle_groups": ["chest", "triceps", "shoulders"],
        "equipment": "barbell",
    },
    {
        "name": "Dumbbell Bench Press",
        "category": "compound",
        "muscle_groups": ["chest", "triceps", "shoulders"],
        "equipment": "dumbbells",
    },
    {
        "name": "Incline Dumbbell Press",
        "category": "compound",
        "muscle_groups": ["chest", "triceps", "shoulders"],
        "equipment": "dumbbells",
    },
    {
        "name": "Dumbbell Fly",
        "category": "isolation",
        "muscle_groups": ["chest"],
        "equipment": "dumbbells",
    },
    {
        "name": "Cable Fly",
        "category": "isolation",
        "muscle_groups": ["chest"],
        "equipment": "cable",
    },
    {
        "name": "Push Up",
        "category": "compound",
        "muscle_groups": ["chest", "triceps", "shoulders"],
        "equipment": "bodyweight",
    },
    {
        "name": "Chest Dip",
        "category": "compound",
        "muscle_groups": ["chest", "triceps"],
        "equipment": "bodyweight",
    },
    # --- Back ---
    {
        "name": "Barbell Row",
        "category": "compound",
        "muscle_groups": ["back", "biceps"],
        "equipment": "barbell",
    },
    {
        "name": "Dumbbell Row",
        "category": "compound",
        "muscle_groups": ["back", "biceps"],
        "equipment": "dumbbells",
    },
    {
        "name": "Pull Up",
        "category": "compound",
        "muscle_groups": ["back", "biceps"],
        "equipment": "bodyweight",
    },
    {
        "name": "Chin Up",
        "category": "compound",
        "muscle_groups": ["back", "biceps"],
        "equipment": "bodyweight",
    },
    {
        "name": "Lat Pulldown",
        "category": "compound",
        "muscle_groups": ["back", "biceps"],
        "equipment": "cable",
    },
    {
        "name": "Seated Cable Row",
        "category": "compound",
        "muscle_groups": ["back", "biceps"],
        "equipment": "cable",
    },
    {
        "name": "T-Bar Row",
        "category": "compound",
        "muscle_groups": ["back", "biceps"],
        "equipment": "barbell",
    },
    {
        "name": "Face Pull",
        "category": "isolation",
        "muscle_groups": ["back", "shoulders"],
        "equipment": "cable",
    },
    # --- Shoulders ---
    {
        "name": "Overhead Press",
        "category": "compound",
        "muscle_groups": ["shoulders", "triceps"],
        "equipment": "barbell",
    },
    {
        "name": "Dumbbell Shoulder Press",
        "category": "compound",
        "muscle_groups": ["shoulders", "triceps"],
        "equipment": "dumbbells",
    },
    {
        "name": "Lateral Raise",
        "category": "isolation",
        "muscle_groups": ["shoulders"],
        "equipment": "dumbbells",
    },
    {
        "name": "Front Raise",
        "category": "isolation",
        "muscle_groups": ["shoulders"],
        "equipment": "dumbbells",
    },
    {
        "name": "Reverse Fly",
        "category": "isolation",
        "muscle_groups": ["shoulders", "back"],
        "equipment": "dumbbells",
    },
    {
        "name": "Arnold Press",
        "category": "compound",
        "muscle_groups": ["shoulders", "triceps"],
        "equipment": "dumbbells",
    },
    # --- Legs ---
    {
        "name": "Barbell Squat",
        "category": "compound",
        "muscle_groups": ["quads", "glutes", "hamstrings"],
        "equipment": "barbell",
    },
    {
        "name": "Front Squat",
        "category": "compound",
        "muscle_groups": ["quads", "glutes"],
        "equipment": "barbell",
    },
    {
        "name": "Leg Press",
        "category": "compound",
        "muscle_groups": ["quads", "glutes"],
        "equipment": "machine",
    },
    {
        "name": "Romanian Deadlift",
        "category": "compound",
        "muscle_groups": ["hamstrings", "glutes", "back"],
        "equipment": "barbell",
    },
    {
        "name": "Leg Curl",
        "category": "isolation",
        "muscle_groups": ["hamstrings"],
        "equipment": "machine",
    },
    {
        "name": "Leg Extension",
        "category": "isolation",
        "muscle_groups": ["quads"],
        "equipment": "machine",
    },
    {
        "name": "Bulgarian Split Squat",
        "category": "compound",
        "muscle_groups": ["quads", "glutes"],
        "equipment": "dumbbells",
    },
    {
        "name": "Walking Lunge",
        "category": "compound",
        "muscle_groups": ["quads", "glutes"],
        "equipment": "dumbbells",
    },
    {
        "name": "Calf Raise",
        "category": "isolation",
        "muscle_groups": ["calves"],
        "equipment": "machine",
    },
    {
        "name": "Hip Thrust",
        "category": "compound",
        "muscle_groups": ["glutes", "hamstrings"],
        "equipment": "barbell",
    },
    {
        "name": "Goblet Squat",
        "category": "compound",
        "muscle_groups": ["quads", "glutes"],
        "equipment": "dumbbells",
    },
    # --- Arms ---
    {
        "name": "Barbell Curl",
        "category": "isolation",
        "muscle_groups": ["biceps"],
        "equipment": "barbell",
    },
    {
        "name": "Dumbbell Curl",
        "category": "isolation",
        "muscle_groups": ["biceps"],
        "equipment": "dumbbells",
    },
    {
        "name": "Hammer Curl",
        "category": "isolation",
        "muscle_groups": ["biceps", "forearms"],
        "equipment": "dumbbells",
    },
    {
        "name": "Preacher Curl",
        "category": "isolation",
        "muscle_groups": ["biceps"],
        "equipment": "barbell",
    },
    {
        "name": "Tricep Pushdown",
        "category": "isolation",
        "muscle_groups": ["triceps"],
        "equipment": "cable",
    },
    {
        "name": "Overhead Tricep Extension",
        "category": "isolation",
        "muscle_groups": ["triceps"],
        "equipment": "dumbbells",
    },
    {
        "name": "Skull Crusher",
        "category": "isolation",
        "muscle_groups": ["triceps"],
        "equipment": "barbell",
    },
    {
        "name": "Close Grip Bench Press",
        "category": "compound",
        "muscle_groups": ["triceps", "chest"],
        "equipment": "barbell",
    },
    # --- Core ---
    {
        "name": "Plank",
        "category": "isolation",
        "muscle_groups": ["core"],
        "equipment": "bodyweight",
    },
    {
        "name": "Hanging Leg Raise",
        "category": "isolation",
        "muscle_groups": ["core"],
        "equipment": "bodyweight",
    },
    {
        "name": "Cable Crunch",
        "category": "isolation",
        "muscle_groups": ["core"],
        "equipment": "cable",
    },
    {
        "name": "Ab Wheel Rollout",
        "category": "isolation",
        "muscle_groups": ["core"],
        "equipment": "bodyweight",
    },
    # --- Full Body / Compound ---
    {
        "name": "Deadlift",
        "category": "compound",
        "muscle_groups": ["back", "glutes", "hamstrings", "quads"],
        "equipment": "barbell",
    },
    {
        "name": "Sumo Deadlift",
        "category": "compound",
        "muscle_groups": ["back", "glutes", "hamstrings", "quads"],
        "equipment": "barbell",
    },
    {
        "name": "Power Clean",
        "category": "compound",
        "muscle_groups": ["back", "shoulders", "quads", "glutes"],
        "equipment": "barbell",
    },
    {
        "name": "Kettlebell Swing",
        "category": "compound",
        "muscle_groups": ["glutes", "hamstrings", "back"],
        "equipment": "kettlebell",
    },
    # --- Cardio ---
    {
        "name": "Treadmill Running",
        "category": "cardio",
        "muscle_groups": ["quads", "hamstrings", "calves"],
        "equipment": "machine",
    },
    {
        "name": "Rowing Machine",
        "category": "cardio",
        "muscle_groups": ["back", "quads", "shoulders"],
        "equipment": "machine",
    },
    {
        "name": "Cycling",
        "category": "cardio",
        "muscle_groups": ["quads", "hamstrings", "calves"],
        "equipment": "machine",
    },
    {
        "name": "Jump Rope",
        "category": "cardio",
        "muscle_groups": ["calves", "shoulders"],
        "equipment": "bodyweight",
    },
]


async def seed_built_in_exercises(db: AsyncSession) -> int:
    """Insert built-in exercises if not already present. Returns count of inserted exercises."""
    result = await db.execute(
        select(Exercise.name).where(Exercise.user_id == None)  # noqa: E711
    )
    existing_names = {row[0] for row in result.all()}

    count = 0
    for ex_data in BUILT_IN_EXERCISES:
        if ex_data["name"] not in existing_names:
            exercise = Exercise(
                user_id=None,
                name=ex_data["name"],
                category=ex_data["category"],
                muscle_groups=ex_data["muscle_groups"],
                equipment=ex_data["equipment"],
                is_custom=False,
            )
            db.add(exercise)
            count += 1

    if count > 0:
        await db.flush()

    return count

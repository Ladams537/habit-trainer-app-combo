from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.api.dependencies import DB, CurrentUser
from src.modules.fitness.schemas import (
    AddExerciseRequest,
    CompleteSessionRequest,
    ExerciseCreate,
    ExerciseProgressionPoint,
    ExerciseResponse,
    ExerciseSetsGroup,
    ExerciseStatsResponse,
    OverviewStatsResponse,
    StartSessionRequest,
    WorkoutSessionResponse,
    WorkoutSessionSummary,
    WorkoutSetCreate,
    WorkoutSetResponse,
    WorkoutTemplateCreate,
    WorkoutTemplateResponse,
    WorkoutTemplateUpdate,
)
from src.modules.fitness.service import FitnessService

router = APIRouter(prefix="/api/fitness", tags=["fitness"])


def _session_to_response(session) -> WorkoutSessionResponse:
    """Convert a WorkoutSession ORM object to a response with grouped exercises."""
    groups: dict[UUID, ExerciseSetsGroup] = {}
    for ws in session.sets:
        eid = ws.exercise_id
        if eid not in groups:
            groups[eid] = ExerciseSetsGroup(
                exercise=ExerciseResponse.model_validate(ws.exercise),
                sets=[],
            )
        groups[eid].sets.append(WorkoutSetResponse.model_validate(ws))

    return WorkoutSessionResponse(
        id=session.id,
        user_id=session.user_id,
        template_id=session.template_id,
        started_at=session.started_at,
        completed_at=session.completed_at,
        notes=session.notes,
        status=session.status,
        template_name=session.template.name if session.template else None,
        exercise_groups=list(groups.values()),
        rating_energy=session.rating_energy,
        rating_mood=session.rating_mood,
    )


def _session_to_summary(session) -> WorkoutSessionSummary:
    """Convert a WorkoutSession ORM object to a summary."""
    exercise_ids = set()
    total_sets = 0
    total_volume = 0.0
    for ws in session.sets:
        exercise_ids.add(ws.exercise_id)
        if ws.completed:
            total_sets += 1
            total_volume += ws.weight_kg * ws.reps

    return WorkoutSessionSummary(
        id=session.id,
        template_id=session.template_id,
        started_at=session.started_at,
        completed_at=session.completed_at,
        status=session.status,
        template_name=session.template.name if session.template else None,
        exercise_count=len(exercise_ids),
        total_sets=total_sets,
        total_volume=total_volume,
        rating_energy=session.rating_energy,
        rating_mood=session.rating_mood,
    )


# --- Exercises ---

@router.get("/exercises", response_model=list[ExerciseResponse])
async def list_exercises(
    user: CurrentUser,
    db: DB,
    category: str | None = Query(None),
    muscle_group: str | None = Query(None),
):
    service = FitnessService(db)
    return await service.list_exercises(user.id, category=category, muscle_group=muscle_group)


@router.post("/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise(data: ExerciseCreate, user: CurrentUser, db: DB):
    service = FitnessService(db)
    return await service.create_exercise(user.id, data)


# --- Templates ---

@router.get("/templates", response_model=list[WorkoutTemplateResponse])
async def list_templates(user: CurrentUser, db: DB):
    service = FitnessService(db)
    return await service.list_templates(user.id)


@router.post("/templates", response_model=WorkoutTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(data: WorkoutTemplateCreate, user: CurrentUser, db: DB):
    service = FitnessService(db)
    return await service.create_template(user.id, data)


@router.get("/templates/{template_id}", response_model=WorkoutTemplateResponse)
async def get_template(template_id: UUID, user: CurrentUser, db: DB):
    service = FitnessService(db)
    template = await service.get_template(user.id, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/templates/{template_id}", response_model=WorkoutTemplateResponse)
async def update_template(template_id: UUID, data: WorkoutTemplateUpdate, user: CurrentUser, db: DB):
    service = FitnessService(db)
    template = await service.update_template(user.id, template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: UUID, user: CurrentUser, db: DB):
    service = FitnessService(db)
    if not await service.delete_template(user.id, template_id):
        raise HTTPException(status_code=404, detail="Template not found")


# --- Sessions ---

@router.post("/sessions/start", response_model=WorkoutSessionResponse)
async def start_session(data: StartSessionRequest, user: CurrentUser, db: DB):
    service = FitnessService(db)
    session = await service.start_session(user.id, data)
    # Reload with relationships
    session = await service.get_session(user.id, session.id)
    return _session_to_response(session)


@router.get("/sessions/active", response_model=WorkoutSessionResponse | None)
async def get_active_session(user: CurrentUser, db: DB):
    service = FitnessService(db)
    session = await service.get_active_session(user.id)
    if not session:
        return None
    return _session_to_response(session)


@router.get("/sessions", response_model=list[WorkoutSessionSummary])
async def list_sessions(
    user: CurrentUser,
    db: DB,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    service = FitnessService(db)
    sessions = await service.list_sessions(user.id, limit=limit, offset=offset)
    return [_session_to_summary(s) for s in sessions]


@router.get("/sessions/{session_id}", response_model=WorkoutSessionResponse)
async def get_session(session_id: UUID, user: CurrentUser, db: DB):
    service = FitnessService(db)
    session = await service.get_session(user.id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_to_response(session)


@router.post("/sessions/{session_id}/sets", response_model=WorkoutSetResponse, status_code=status.HTTP_201_CREATED)
async def log_set(session_id: UUID, data: WorkoutSetCreate, user: CurrentUser, db: DB):
    service = FitnessService(db)
    try:
        return await service.log_set(user.id, session_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/sessions/{session_id}/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_set(session_id: UUID, set_id: UUID, user: CurrentUser, db: DB):
    service = FitnessService(db)
    if not await service.delete_set(user.id, session_id, set_id):
        raise HTTPException(status_code=404, detail="Set not found")


@router.post("/sessions/{session_id}/exercises", status_code=status.HTTP_204_NO_CONTENT)
async def add_exercise_to_session(session_id: UUID, data: AddExerciseRequest, user: CurrentUser, db: DB):
    """Add an exercise to a free-form session (no-op, just validates session exists)."""
    service = FitnessService(db)
    session = await service.get_session(user.id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Session is not in progress")


@router.post("/sessions/{session_id}/complete", response_model=WorkoutSessionResponse)
async def complete_session(
    session_id: UUID, user: CurrentUser, db: DB, data: CompleteSessionRequest | None = None
):
    service = FitnessService(db)
    notes = data.notes if data else None
    rating_energy = data.rating_energy if data else None
    rating_mood = data.rating_mood if data else None
    session = await service.complete_session(
        user.id, session_id, notes=notes,
        rating_energy=rating_energy, rating_mood=rating_mood,
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_to_response(session)


# --- Stats ---

@router.get("/exercises/{exercise_id}/history")
async def exercise_history(
    exercise_id: UUID,
    user: CurrentUser,
    db: DB,
    limit: int = Query(10, ge=1, le=50),
):
    service = FitnessService(db)
    return await service.get_exercise_history(user.id, exercise_id, limit=limit)


@router.get("/exercises/{exercise_id}/progression", response_model=ExerciseStatsResponse)
async def exercise_progression(
    exercise_id: UUID,
    user: CurrentUser,
    db: DB,
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
):
    service = FitnessService(db)
    exercise = await service.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    progression = await service.get_exercise_progression(
        user.id, exercise_id, from_date=from_date, to_date=to_date
    )
    pr_weight = max((p["max_weight"] for p in progression), default=0)
    total_volume = sum(p["volume"] for p in progression)

    return ExerciseStatsResponse(
        exercise=ExerciseResponse.model_validate(exercise),
        progression=[ExerciseProgressionPoint(**p) for p in progression],
        total_sessions=len(progression),
        pr_weight=pr_weight,
        total_volume=total_volume,
    )


@router.get("/stats/trained-exercises", response_model=list[ExerciseResponse])
async def trained_exercises(user: CurrentUser, db: DB):
    service = FitnessService(db)
    return await service.get_trained_exercises(user.id)


@router.get("/stats/overview", response_model=OverviewStatsResponse)
async def overview_stats(
    user: CurrentUser,
    db: DB,
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
):
    service = FitnessService(db)
    return await service.get_overview_stats(user.id, from_date=from_date, to_date=to_date)

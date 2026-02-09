from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.dependencies import DB, CurrentUser
from src.modules.skills.schemas import (
    CompetencyLevelResponse,
    PracticeSessionCreate,
    PracticeSessionResponse,
    SkillCreate,
    SkillProgressResponse,
    SkillResponse,
    SkillScheduleResponse,
    SkillTodayResponse,
    SkillUpdate,
    SubSkillSchedule,
)
from src.modules.skills.service import SkillsService

router = APIRouter(prefix="/api/skills", tags=["skills"])


# --- Skills CRUD ---


@router.get("/", response_model=list[SkillResponse])
async def list_skills(user: CurrentUser, db: DB):
    service = SkillsService(db)
    return await service.list_skills(user.id)


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(data: SkillCreate, user: CurrentUser, db: DB):
    service = SkillsService(db)
    return await service.create_skill(user.id, data)


# /today must be before /{skill_id} to avoid UUID parse conflict
@router.get("/today", response_model=list[SkillTodayResponse])
async def skills_due_today(user: CurrentUser, db: DB):
    service = SkillsService(db)
    return await service.get_skills_due_today(user.id)


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: UUID, user: CurrentUser, db: DB):
    service = SkillsService(db)
    skill = await service.get_skill(user.id, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: UUID, data: SkillUpdate, user: CurrentUser, db: DB):
    service = SkillsService(db)
    skill = await service.update_skill(user.id, skill_id, data)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: UUID, user: CurrentUser, db: DB):
    service = SkillsService(db)
    if not await service.delete_skill(user.id, skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")


# --- Practice ---


@router.post(
    "/{skill_id}/practice",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def log_practice(
    skill_id: UUID, data: PracticeSessionCreate, user: CurrentUser, db: DB
):
    service = SkillsService(db)
    try:
        return await service.log_practice(user.id, skill_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- Progress / Schedule ---


@router.get("/{skill_id}/progress", response_model=SkillProgressResponse)
async def get_progress(skill_id: UUID, user: CurrentUser, db: DB):
    service = SkillsService(db)
    result = await service.get_progress(user.id, skill_id)
    if not result:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillProgressResponse(
        skill=SkillResponse.model_validate(result["skill"]),
        competency_levels=[
            CompetencyLevelResponse(**cl) for cl in result["competency_levels"]
        ],
        recent_sessions=[
            PracticeSessionResponse.model_validate(s) for s in result["recent_sessions"]
        ],
    )


@router.get("/{skill_id}/schedule", response_model=SkillScheduleResponse)
async def get_schedule(skill_id: UUID, user: CurrentUser, db: DB):
    service = SkillsService(db)
    result = await service.get_schedule(user.id, skill_id)
    if not result:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillScheduleResponse(
        skill=SkillResponse.model_validate(result["skill"]),
        schedule=[SubSkillSchedule(**s) for s in result["schedule"]],
    )

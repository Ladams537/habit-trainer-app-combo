from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.habits.models import ActivityLog
from src.modules.skills.fsrs import (
    compute_retrievability,
    is_due_for_review,
    update_fsrs_params,
)
from src.modules.skills.models import CompetencyLevel, PracticeSession, SkillDefinition
from src.modules.skills.schemas import PracticeSessionCreate, SkillCreate, SkillUpdate


class SkillsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- CRUD ---

    async def create_skill(self, user_id: UUID, data: SkillCreate) -> SkillDefinition:
        skill = SkillDefinition(
            user_id=user_id,
            name=data.name,
            category=data.category,
            sub_skills=data.sub_skills,
            current_level=data.current_level,
        )
        self.db.add(skill)
        await self.db.flush()

        # Create CompetencyLevel rows for each sub-skill
        for sub in data.sub_skills:
            cl = CompetencyLevel(skill_id=skill.id, sub_skill=sub)
            self.db.add(cl)

        await self.db.flush()
        await self.db.refresh(skill)
        return skill

    async def list_skills(self, user_id: UUID) -> list[SkillDefinition]:
        result = await self.db.execute(
            select(SkillDefinition)
            .where(SkillDefinition.user_id == user_id, SkillDefinition.is_active == True)  # noqa: E712
            .order_by(SkillDefinition.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_skill(self, user_id: UUID, skill_id: UUID) -> SkillDefinition | None:
        result = await self.db.execute(
            select(SkillDefinition)
            .where(SkillDefinition.id == skill_id, SkillDefinition.user_id == user_id)
            .options(
                selectinload(SkillDefinition.competency_levels),
                selectinload(SkillDefinition.practice_sessions),
            )
        )
        return result.scalar_one_or_none()

    async def update_skill(
        self, user_id: UUID, skill_id: UUID, data: SkillUpdate
    ) -> SkillDefinition | None:
        skill = await self.get_skill(user_id, skill_id)
        if not skill:
            return None

        if data.name is not None:
            skill.name = data.name
        if data.category is not None:
            skill.category = data.category
        if data.current_level is not None:
            skill.current_level = data.current_level

        if data.sub_skills is not None:
            skill.sub_skills = data.sub_skills
            # Add CompetencyLevel rows for new sub-skills (preserve existing)
            existing = {cl.sub_skill for cl in skill.competency_levels}
            for sub in data.sub_skills:
                if sub not in existing:
                    cl = CompetencyLevel(skill_id=skill.id, sub_skill=sub)
                    self.db.add(cl)

        await self.db.flush()
        return await self.get_skill(user_id, skill_id)

    async def delete_skill(self, user_id: UUID, skill_id: UUID) -> bool:
        """Soft delete — sets is_active=False."""
        skill = await self.get_skill(user_id, skill_id)
        if not skill:
            return False
        skill.is_active = False
        await self.db.flush()
        return True

    # --- Practice ---

    async def log_practice(
        self, user_id: UUID, skill_id: UUID, data: PracticeSessionCreate
    ) -> PracticeSession:
        skill = await self.get_skill(user_id, skill_id)
        if not skill:
            raise ValueError("Skill not found")

        # Create ActivityLog entry
        activity = ActivityLog(
            user_id=user_id,
            domain="skills",
            duration_seconds=data.duration_minutes * 60,
            notes=data.notes,
        )
        self.db.add(activity)
        await self.db.flush()

        # Create PracticeSession
        session = PracticeSession(
            skill_id=skill_id,
            activity_id=activity.id,
            duration_minutes=data.duration_minutes,
            quality_rating=data.quality_rating,
            focus_area=data.focus_area,
            notes=data.notes,
        )
        self.db.add(session)

        # Update FSRS competency levels
        await self._update_competency(skill, data.focus_area, data.quality_rating)

        # Increment total practice minutes
        skill.total_practice_minutes += data.duration_minutes

        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def _update_competency(
        self, skill: SkillDefinition, focus_area: str | None, quality: int
    ) -> None:
        """Update FSRS params for the practiced sub-skills."""
        now = datetime.now(timezone.utc)

        for cl in skill.competency_levels:
            # If a focus_area is specified, only update that sub-skill
            if focus_area and cl.sub_skill != focus_area:
                continue

            new_d, new_s, next_review = update_fsrs_params(
                cl.difficulty, cl.stability, quality
            )
            cl.difficulty = new_d
            cl.stability = new_s
            cl.last_review_date = now
            cl.next_review_date = next_review
            cl.review_count += 1

    # --- Progress / Schedule ---

    async def get_progress(
        self, user_id: UUID, skill_id: UUID
    ) -> dict | None:
        skill = await self.get_skill(user_id, skill_id)
        if not skill:
            return None

        now = datetime.now(timezone.utc)
        competency_data = []
        for cl in skill.competency_levels:
            days_elapsed = 0.0
            if cl.last_review_date:
                days_elapsed = (now - cl.last_review_date).total_seconds() / 86400
            r = compute_retrievability(cl.stability, days_elapsed)
            competency_data.append({
                "id": cl.id,
                "skill_id": cl.skill_id,
                "sub_skill": cl.sub_skill,
                "difficulty": cl.difficulty,
                "stability": cl.stability,
                "last_review_date": cl.last_review_date,
                "next_review_date": cl.next_review_date,
                "review_count": cl.review_count,
                "retrievability": round(r, 3),
            })

        # Recent sessions (last 10)
        recent = sorted(
            skill.practice_sessions, key=lambda s: s.practiced_at, reverse=True
        )[:10]

        return {
            "skill": skill,
            "competency_levels": competency_data,
            "recent_sessions": recent,
        }

    async def get_schedule(
        self, user_id: UUID, skill_id: UUID
    ) -> dict | None:
        skill = await self.get_skill(user_id, skill_id)
        if not skill:
            return None

        now = datetime.now(timezone.utc)
        schedule = []
        for cl in skill.competency_levels:
            days_elapsed = 0.0
            if cl.last_review_date:
                days_elapsed = (now - cl.last_review_date).total_seconds() / 86400
            r = compute_retrievability(cl.stability, days_elapsed)
            schedule.append({
                "sub_skill": cl.sub_skill,
                "next_review_date": cl.next_review_date,
                "retrievability": round(r, 3),
                "is_due": is_due_for_review(cl.next_review_date),
            })

        return {"skill": skill, "schedule": schedule}

    async def get_skills_due_today(self, user_id: UUID) -> list[dict]:
        """Get skills with at least one sub-skill due for review."""
        skills = await self.list_skills(user_id)

        result = []
        for skill in skills:
            # Need competency levels — reload with relationships
            full_skill = await self.get_skill(user_id, skill.id)
            if not full_skill:
                continue

            due_count = sum(
                1 for cl in full_skill.competency_levels
                if is_due_for_review(cl.next_review_date)
            )
            if due_count > 0:
                result.append({
                    "id": full_skill.id,
                    "name": full_skill.name,
                    "category": full_skill.category,
                    "due_count": due_count,
                    "total_practice_minutes": full_skill.total_practice_minutes,
                })

        return result

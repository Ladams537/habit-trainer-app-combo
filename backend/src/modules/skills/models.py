import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.base_models import Base, TimestampMixin, UUIDMixin


class SkillDefinition(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skill_definitions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, server_default="'general'")
    sub_skills: Mapped[list] = mapped_column(JSONB, server_default="[]")
    current_level: Mapped[str] = mapped_column(String(20), server_default="'beginner'")
    total_practice_minutes: Mapped[int] = mapped_column(Integer, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")

    practice_sessions: Mapped[list["PracticeSession"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )
    competency_levels: Mapped[list["CompetencyLevel"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_skill_definitions_user_active", "user_id", "is_active"),
    )


class PracticeSession(Base, UUIDMixin):
    __tablename__ = "practice_sessions"

    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill_definitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    activity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("activity_log.id")
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    quality_rating: Mapped[int] = mapped_column(
        SmallInteger,
        CheckConstraint("quality_rating BETWEEN 1 AND 5"),
        nullable=False,
    )
    focus_area: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    practiced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    skill: Mapped[SkillDefinition] = relationship(back_populates="practice_sessions")

    __table_args__ = (
        Index("idx_practice_sessions_skill", "skill_id"),
    )


class CompetencyLevel(Base, UUIDMixin):
    __tablename__ = "competency_levels"

    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill_definitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    sub_skill: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, server_default="5.0")
    stability: Mapped[float] = mapped_column(Float, server_default="1.0")
    last_review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_count: Mapped[int] = mapped_column(Integer, server_default="0")

    skill: Mapped[SkillDefinition] = relationship(back_populates="competency_levels")

    __table_args__ = (
        Index("idx_competency_levels_skill", "skill_id"),
        Index("idx_competency_levels_next_review", "next_review_date"),
    )

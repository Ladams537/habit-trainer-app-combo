import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.base_models import Base, UUIDMixin


class ActivityLog(Base, UUIDMixin):
    __tablename__ = "activity_log"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    domain: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("domain IN ('fitness', 'skills', 'habits')"),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    energy_level: Mapped[int | None] = mapped_column(
        SmallInteger, CheckConstraint("energy_level BETWEEN 1 AND 10")
    )
    mood: Mapped[int | None] = mapped_column(
        SmallInteger, CheckConstraint("mood BETWEEN 1 AND 10")
    )
    notes: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (Index("idx_activity_user_day", "user_id", started_at.desc()),)


class HabitDefinition(Base, UUIDMixin):
    __tablename__ = "habit_definitions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    habit_type: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("habit_type IN ('boolean', 'numeric', 'duration')"),
        nullable=False,
    )
    frequency: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="daily"
    )
    frequency_config: Mapped[dict] = mapped_column(JSONB, server_default="{}")
    target_value: Mapped[float] = mapped_column(Numeric, server_default="1")
    unit: Mapped[str | None] = mapped_column(String(50))
    color: Mapped[str] = mapped_column(String(20), server_default="'#4CAF50'")
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0")
    partial_completion_counts: Mapped[bool] = mapped_column(
        Boolean, server_default="true"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    completions: Mapped[list["HabitCompletion"]] = relationship(back_populates="habit")

    __table_args__ = (
        Index("idx_habit_definitions_user_active", "user_id", "is_active"),
    )


class HabitCompletion(Base, UUIDMixin):
    __tablename__ = "habit_completions"

    activity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("activity_log.id")
    )
    habit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("habit_definitions.id"), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    value: Mapped[float] = mapped_column(Numeric, server_default="1")
    completed: Mapped[bool] = mapped_column(Boolean, server_default="true")

    habit: Mapped[HabitDefinition] = relationship(back_populates="completions")

    __table_args__ = (
        Index("idx_habit_completions_habit_date", "habit_id", completed_at.desc()),
    )

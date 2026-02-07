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


class Exercise(Base, UUIDMixin):
    __tablename__ = "exercises"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("category IN ('compound', 'isolation', 'cardio')"),
        nullable=False,
    )
    muscle_groups: Mapped[list] = mapped_column(JSONB, server_default="[]")
    equipment: Mapped[str | None] = mapped_column(String(100))
    is_custom: Mapped[bool] = mapped_column(Boolean, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_exercises_user", "user_id"),
        Index("idx_exercises_category", "category"),
    )


class WorkoutTemplate(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workout_templates"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    exercises: Mapped[list["TemplateExercise"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateExercise.sort_order",
    )

    __table_args__ = (
        Index("idx_workout_templates_user", "user_id"),
    )


class TemplateExercise(Base, UUIDMixin):
    __tablename__ = "template_exercises"

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_templates.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0")
    target_sets: Mapped[int] = mapped_column(Integer, server_default="3")
    target_reps: Mapped[int] = mapped_column(Integer, server_default="10")
    target_weight_kg: Mapped[float | None] = mapped_column(Float)
    set_type: Mapped[str] = mapped_column(String(20), server_default="'working'")
    rest_seconds: Mapped[int] = mapped_column(Integer, server_default="120")

    template: Mapped[WorkoutTemplate] = relationship(back_populates="exercises")
    exercise: Mapped[Exercise] = relationship()

    __table_args__ = (
        Index("idx_template_exercises_template", "template_id"),
    )


class WorkoutSession(Base, UUIDMixin):
    __tablename__ = "workout_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_templates.id"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('in_progress', 'completed')"),
        server_default="'in_progress'",
    )

    template: Mapped[WorkoutTemplate | None] = relationship()
    sets: Mapped[list["WorkoutSet"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="WorkoutSet.logged_at",
    )

    __table_args__ = (
        Index("idx_workout_sessions_user", "user_id"),
        Index("idx_workout_sessions_status", "user_id", "status"),
    )


class WorkoutSet(Base, UUIDMixin):
    __tablename__ = "workout_sets"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, server_default="0")
    reps: Mapped[int] = mapped_column(Integer, server_default="0")
    rpe: Mapped[int | None] = mapped_column(
        SmallInteger, CheckConstraint("rpe BETWEEN 1 AND 10")
    )
    set_type: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("set_type IN ('warmup', 'working', 'drop', 'failure')"),
        server_default="'working'",
    )
    completed: Mapped[bool] = mapped_column(Boolean, server_default="false")
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped[WorkoutSession] = relationship(back_populates="sets")
    exercise: Mapped[Exercise] = relationship()

    __table_args__ = (
        Index("idx_workout_sets_session", "session_id"),
        Index("idx_workout_sets_exercise", "exercise_id"),
    )

"""initial schema: users, activity_log, habits

Revision ID: 3619fa0c70a6
Revises:
Create Date: 2026-02-06 14:06:32.902104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3619fa0c70a6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('preferences', postgresql.JSONB(), server_default='{}', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'activity_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain', sa.String(20), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('energy_level', sa.SmallInteger(), nullable=True),
        sa.Column('mood', sa.SmallInteger(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.CheckConstraint("domain IN ('fitness', 'skills', 'habits')"),
        sa.CheckConstraint('energy_level BETWEEN 1 AND 10'),
        sa.CheckConstraint('mood BETWEEN 1 AND 10'),
    )
    op.create_index('idx_activity_user_day', 'activity_log', ['user_id', sa.text('started_at DESC')])

    op.create_table(
        'habit_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('habit_type', sa.String(20), nullable=False),
        sa.Column('frequency', sa.String(20), nullable=False, server_default='daily'),
        sa.Column('frequency_config', postgresql.JSONB(), server_default='{}', nullable=True),
        sa.Column('target_value', sa.Numeric(), server_default='1', nullable=True),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('color', sa.String(20), server_default="'#4CAF50'", nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.CheckConstraint("habit_type IN ('boolean', 'numeric', 'duration')"),
    )
    op.create_index('idx_habit_definitions_user_active', 'habit_definitions', ['user_id', 'is_active'])

    op.create_table(
        'habit_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('activity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('habit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('value', sa.Numeric(), server_default='1', nullable=True),
        sa.Column('completed', sa.Boolean(), server_default='true', nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['activity_id'], ['activity_log.id']),
        sa.ForeignKeyConstraint(['habit_id'], ['habit_definitions.id']),
    )
    op.create_index('idx_habit_completions_habit_date', 'habit_completions', ['habit_id', sa.text('completed_at DESC')])


def downgrade() -> None:
    op.drop_table('habit_completions')
    op.drop_table('habit_definitions')
    op.drop_table('activity_log')
    op.drop_table('users')

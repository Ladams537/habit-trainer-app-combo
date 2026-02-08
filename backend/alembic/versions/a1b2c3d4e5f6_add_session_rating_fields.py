"""add session rating fields

Revision ID: a1b2c3d4e5f6
Revises: 9fb2443e3e2b
Create Date: 2026-02-08 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '9fb2443e3e2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add rating_energy and rating_mood columns to workout_sessions."""
    op.add_column('workout_sessions', sa.Column('rating_energy', sa.SmallInteger(), nullable=True))
    op.add_column('workout_sessions', sa.Column('rating_mood', sa.SmallInteger(), nullable=True))
    op.create_check_constraint(
        'ck_workout_sessions_rating_energy',
        'workout_sessions',
        'rating_energy BETWEEN 1 AND 5',
    )
    op.create_check_constraint(
        'ck_workout_sessions_rating_mood',
        'workout_sessions',
        'rating_mood BETWEEN 1 AND 5',
    )


def downgrade() -> None:
    """Remove rating_energy and rating_mood columns from workout_sessions."""
    op.drop_constraint('ck_workout_sessions_rating_mood', 'workout_sessions', type_='check')
    op.drop_constraint('ck_workout_sessions_rating_energy', 'workout_sessions', type_='check')
    op.drop_column('workout_sessions', 'rating_mood')
    op.drop_column('workout_sessions', 'rating_energy')

"""Add judge_metadata to scans

Revision ID: 58cb60a552a2
Revises: fbd0932d8f63
Create Date: 2026-09-03 14:35:51.523583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58cb60a552a2'
down_revision: Union[str, Sequence[str], None] = 'fbd0932d8f63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from sqlalchemy.dialects import postgresql
    op.add_column('scans', sa.Column('judge_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('scans', 'judge_metadata')

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

"""create_notifications_table

Revision ID: 658856ae773e
Revises: 557956ae773e
Create Date: 2026-01-07 08:50:00.000000

"""

revision: str = '658856ae773e'
down_revision: Union[str, None] = '557956ae773e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade () -> None:
    op.create_table ('notifications',
        sa.Column ('id', sa.String (26), nullable=False),
        sa.Column ('user_id', sa.String (26), nullable=False),
        sa.Column ('type', sa.String (255), nullable=False),
        sa.Column ('data', postgresql.JSON (astext_type=sa.Text ()), nullable=False),
        sa.Column ('read_at', sa.DateTime (), nullable=True),
        sa.Column ('created_at', sa.DateTime (), nullable=False),
        sa.Column ('updated_at', sa.DateTime (), nullable=False),
        sa.Column ('deleted_at', sa.DateTime (), nullable=True),
        sa.PrimaryKeyConstraint ('id'),
        sa.ForeignKeyConstraint (['user_id'], ['users.id'], )
    )

    op.create_index (op.f ('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)

def downgrade () -> None:
    op.drop_index (op.f ('ix_notifications_user_id'), table_name='notifications')
    op.drop_table ('notifications')

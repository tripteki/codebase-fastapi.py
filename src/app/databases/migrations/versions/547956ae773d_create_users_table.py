from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

"""create_users_table

Revision ID: 547956ae773d
Revises:
Create Date: 2026-01-05 00:58:51.258644

"""

revision: str = '547956ae773d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade () -> None:
    op.create_table ('users',
        sa.Column ('id', sa.String (26), nullable=False),
        sa.Column ('name', sa.String (255), nullable=False),
        sa.Column ('email', sa.String (255), nullable=False),
        sa.Column ('password', sa.String (255), nullable=False),
        sa.Column ('email_verified_at', sa.DateTime (), nullable=True),
        sa.Column ('created_at', sa.DateTime (), nullable=False),
        sa.Column ('updated_at', sa.DateTime (), nullable=False),
        sa.Column ('deleted_at', sa.DateTime (), nullable=True),
        sa.PrimaryKeyConstraint ('id')
    )

    op.create_index (op.f ('ix_users_email'), 'users', ['email'], unique=True)

def downgrade () -> None:
    op.drop_index (op.f ('ix_users_email'), table_name='users')
    op.drop_table ('users')

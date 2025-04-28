from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

"""create_password_reset_tokens_table

Revision ID: 557956ae773e
Revises: 547956ae773d
Create Date: 2026-01-08 03:00:00.000000

"""

revision: str = '557956ae773e'
down_revision: Union[str, None] = '547956ae773d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade () -> None:
    op.create_table ('password_reset_tokens',
        sa.Column ('token', sa.String (), nullable=False),
        sa.Column ('email', sa.String (), nullable=False),
        sa.Column ('created_at', sa.DateTime (), nullable=False),
        sa.PrimaryKeyConstraint ('token')
    )

    op.create_index (op.f ('ix_password_reset_tokens_email'), 'password_reset_tokens', ['email'], unique=True)
    op.create_foreign_key (
        'password_reset_tokens_email_fkey',
        'password_reset_tokens',
        'users',
        ['email'],
        ['email'],
        ondelete='RESTRICT',
        onupdate='CASCADE'
    )

def downgrade () -> None:
    try:
        op.drop_constraint ('password_reset_tokens_email_fkey', 'password_reset_tokens', type_='foreignkey')
    except Exception:
        pass
    try:
        op.drop_index (op.f ('ix_password_reset_tokens_email'), table_name='password_reset_tokens')
    except Exception:
        pass
    try:
        op.drop_table ('password_reset_tokens')
    except Exception:
        pass

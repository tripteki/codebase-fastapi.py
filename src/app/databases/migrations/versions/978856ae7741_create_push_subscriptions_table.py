from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

"""create_push_subscriptions_table

Revision ID: 978856ae7741
Revises: 878856ae7740
Create Date: 2026-06-24 12:00:00.000000

"""

revision: str = '978856ae7741'
down_revision: Union[str, None] = '878856ae7740'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade () -> None:
    op.create_table ('push_subscriptions',
        sa.Column ('id', sa.BigInteger (), autoincrement=True, nullable=False),
        sa.Column ('subscribable_id', sa.String (length=26), nullable=False),
        sa.Column ('subscribable_type', sa.String (length=255), nullable=False),
        sa.Column ('endpoint', sa.String (length=500), nullable=False),
        sa.Column ('public_key', sa.Text (), nullable=True),
        sa.Column ('auth_token', sa.Text (), nullable=True),
        sa.Column ('content_encoding', sa.String (length=255), nullable=True),
        sa.Column ('created_at', sa.DateTime (), nullable=False),
        sa.Column ('updated_at', sa.DateTime (), nullable=False),
        sa.PrimaryKeyConstraint ('id'),
        sa.UniqueConstraint ('endpoint')
    )

    op.create_index ('subscribable_type_id_index', 'push_subscriptions', ['subscribable_type', 'subscribable_id'], unique=False)

def downgrade () -> None:
    op.drop_index ('subscribable_type_id_index', table_name='push_subscriptions')
    op.drop_table ('push_subscriptions')

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

"""create_settings_table

Revision ID: c08856ae7744
Revises: b08856ae7743
Create Date: 2026-10-04 22:05:00.000000

"""

revision: str = "c08856ae7744"
down_revision: Union[str, None] = "b08856ae7743"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade () -> None:
    op.create_table (
        "settings",
        sa.Column ("id", sa.String (26), nullable=False),
        sa.Column ("key", sa.String (255), nullable=False),
        sa.Column ("value", sa.Text (), nullable=True),
        sa.Column ("value_kind", sa.String (16), nullable=False, server_default="text"),
        sa.Column ("created_at", sa.DateTime (), nullable=False),
        sa.Column ("updated_at", sa.DateTime (), nullable=False),
        sa.Column ("deleted_at", sa.DateTime (), nullable=True),
        sa.PrimaryKeyConstraint ("id"),
        sa.UniqueConstraint ("key"),
    )
    op.create_index ("ix_settings_key", "settings", ["key"])

def downgrade () -> None:
    op.drop_index ("ix_settings_key", table_name="settings")
    op.drop_table ("settings")

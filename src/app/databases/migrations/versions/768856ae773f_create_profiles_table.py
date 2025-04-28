from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

"""create_profiles_table

Revision ID: 768856ae773f
Revises: 658856ae773e
Create Date: 2026-06-24 10:00:00.000000

"""

revision: str = "768856ae773f"
down_revision: Union[str, None] = "658856ae773e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade () -> None:
    op.create_table (
        "profiles",
        sa.Column ("id", sa.String (26), nullable=False),
        sa.Column ("user_id", sa.String (26), nullable=False),
        sa.Column ("full_name", sa.String (255), nullable=True),
        sa.Column ("avatar", sa.String (255), nullable=True),
        sa.Column ("interests", postgresql.JSON (astext_type=sa.Text ()), nullable=True),
        sa.Column ("created_at", sa.DateTime (), nullable=False),
        sa.Column ("updated_at", sa.DateTime (), nullable=False),
        sa.ForeignKeyConstraint (["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint ("id"),
        sa.UniqueConstraint ("user_id"),
    )
    op.create_index (op.f ("ix_profiles_user_id"), "profiles", ["user_id"], unique=True)

def downgrade () -> None:
    op.drop_index (op.f ("ix_profiles_user_id"), table_name="profiles")
    op.drop_table ("profiles")

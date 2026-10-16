from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

"""create_activity_log_table

Revision ID: b08856ae7743
Revises: 978856ae7741
Create Date: 2026-10-04 21:55:00.000000

"""

revision: str = "b08856ae7743"
down_revision: Union[str, None] = "978856ae7741"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade () -> None:
    op.create_table (
        "activity_log",
        sa.Column ("id", sa.String (26), nullable=False),
        sa.Column ("log_name", sa.String (255), nullable=True),
        sa.Column ("description", sa.Text (), nullable=False),
        sa.Column ("subject_type", sa.String (255), nullable=True),
        sa.Column ("event", sa.String (255), nullable=True),
        sa.Column ("subject_id", sa.String (26), nullable=True),
        sa.Column ("causer_type", sa.String (255), nullable=True),
        sa.Column ("causer_id", sa.String (26), nullable=True),
        sa.Column ("properties", sa.JSON (), nullable=True),
        sa.Column ("batch_uuid", sa.String (36), nullable=True),
        sa.Column ("created_at", sa.DateTime (), nullable=False),
        sa.Column ("updated_at", sa.DateTime (), nullable=False),
        sa.PrimaryKeyConstraint ("id"),
    )
    op.create_index ("ix_activity_log_log_name", "activity_log", ["log_name"])
    op.create_index ("ix_activity_log_subject", "activity_log", ["subject_type", "subject_id"])
    op.create_index ("ix_activity_log_causer", "activity_log", ["causer_type", "causer_id"])
    op.create_index ("ix_activity_log_created_at", "activity_log", ["created_at"])

def downgrade () -> None:
    op.drop_index ("ix_activity_log_created_at", table_name="activity_log")
    op.drop_index ("ix_activity_log_causer", table_name="activity_log")
    op.drop_index ("ix_activity_log_subject", table_name="activity_log")
    op.drop_index ("ix_activity_log_log_name", table_name="activity_log")
    op.drop_table ("activity_log")

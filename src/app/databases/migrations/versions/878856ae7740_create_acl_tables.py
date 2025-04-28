from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

"""create_acl_tables

Revision ID: 878856ae7740
Revises: 768856ae773f
Create Date: 2026-06-24 12:00:00.000000

"""

revision: str = "878856ae7740"
down_revision: Union[str, None] = "768856ae773f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade () -> None:
    op.create_table (
        "permissions",
        sa.Column ("id", sa.String (26), nullable=False),
        sa.Column ("name", sa.String (255), nullable=False),
        sa.Column ("guard_name", sa.String (255), nullable=False),
        sa.Column ("created_at", sa.DateTime (), nullable=False),
        sa.Column ("updated_at", sa.DateTime (), nullable=False),
        sa.PrimaryKeyConstraint ("id"),
        sa.UniqueConstraint ("name", "guard_name"),
    )

    op.create_table (
        "roles",
        sa.Column ("id", sa.String (26), nullable=False),
        sa.Column ("name", sa.String (255), nullable=False),
        sa.Column ("guard_name", sa.String (255), nullable=False),
        sa.Column ("created_at", sa.DateTime (), nullable=False),
        sa.Column ("updated_at", sa.DateTime (), nullable=False),
        sa.PrimaryKeyConstraint ("id"),
        sa.UniqueConstraint ("name", "guard_name"),
    )

    op.create_table (
        "role_has_permissions",
        sa.Column ("permission_id", sa.String (26), nullable=False),
        sa.Column ("role_id", sa.String (26), nullable=False),
        sa.ForeignKeyConstraint (["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint (["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint ("permission_id", "role_id"),
    )

    op.create_table (
        "model_has_roles",
        sa.Column ("role_id", sa.String (26), nullable=False),
        sa.Column ("model_type", sa.String (255), nullable=False),
        sa.Column ("model_id", sa.String (26), nullable=False),
        sa.ForeignKeyConstraint (["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint ("role_id", "model_type", "model_id"),
    )

    op.create_index ("model_has_roles_model_id_model_type_index", "model_has_roles", ["model_id", "model_type"])

def downgrade () -> None:
    op.drop_index ("model_has_roles_model_id_model_type_index", table_name="model_has_roles")
    op.drop_table ("model_has_roles")
    op.drop_table ("role_has_permissions")
    op.drop_table ("roles")
    op.drop_table ("permissions")

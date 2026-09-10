"""add task assignments and audit timestamps

Revision ID: d7a2_task_assignments
Revises: c3f1_workspace_intelligence
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d7a2_task_assignments"
down_revision: Union[str, Sequence[str], None] = "c3f1_workspace_intelligence"
branch_labels = None
depends_on = None


def _columns(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "task_assignments" not in tables:
        op.create_table(
            "task_assignments",
            sa.Column("id", sa.Uuid(), primary_key=True),
            sa.Column("task_id", sa.Uuid(), nullable=False),
            sa.Column("person_id", sa.Uuid(), nullable=False),
            sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["person_id"], ["people.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("task_id", "person_id"),
        )
        op.create_index("ix_task_assignments_task_id", "task_assignments", ["task_id"])

    for table in ("milestones", "project_risks"):
        columns = _columns(table) if table in tables else set()
        for name in ("created_at", "updated_at"):
            if name not in columns:
                op.add_column(table, sa.Column(name, sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "task_assignments" in inspector.get_table_names():
        op.drop_index("ix_task_assignments_task_id", table_name="task_assignments")
        op.drop_table("task_assignments")
    for table in ("project_risks", "milestones"):
        columns = _columns(table)
        for name in ("updated_at", "created_at"):
            if name in columns:
                op.drop_column(table, name)

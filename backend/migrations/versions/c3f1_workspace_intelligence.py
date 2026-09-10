"""add workspace intelligence entities

Revision ID: c3f1_workspace_intelligence
Revises: f9b58b1780af
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3f1_workspace_intelligence"
down_revision: Union[str, Sequence[str], None] = "f9b58b1780af"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("project_workspace_metadata", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("project_id", sa.Uuid(), nullable=False), sa.Column("domain", sa.String(80), nullable=False, server_default="Software"), sa.Column("status_reason", sa.Text(), nullable=False, server_default=""), sa.Column("status_description", sa.Text(), nullable=False, server_default=""), sa.Column("expected_timeline", sa.String(120), nullable=False, server_default="12 weeks"), sa.Column("health_score", sa.Integer(), nullable=False, server_default="78"), sa.Column("progress", sa.Integer(), nullable=False, server_default="0"), sa.Column("executive_summary", sa.Text(), nullable=False, server_default=""), sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"), sa.UniqueConstraint("project_id"))
    op.create_table("people", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(180), nullable=False), sa.Column("title", sa.String(120), nullable=False, server_default="Project contributor"), sa.Column("avatar", sa.String(30)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.UniqueConstraint("email"))
    op.create_table("project_memberships", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("project_id", sa.Uuid(), nullable=False), sa.Column("person_id", sa.Uuid(), nullable=False), sa.Column("role_title", sa.String(100), nullable=False), sa.Column("workload_percent", sa.Integer(), nullable=False, server_default="60"), sa.Column("modules_json", sa.JSON(), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["person_id"], ["people.id"], ondelete="CASCADE"), sa.UniqueConstraint("project_id", "person_id"))
    op.create_index("ix_project_memberships_project_id", "project_memberships", ["project_id"])
    op.create_table("reports", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("project_id", sa.Uuid(), nullable=False), sa.Column("report_type", sa.String(50), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("summary", sa.Text(), nullable=False), sa.Column("generated_by", sa.String(40), nullable=False, server_default="mock-ai"), sa.Column("status", sa.String(30), nullable=False, server_default="generated"), sa.Column("score", sa.Integer()), sa.Column("content", sa.Text(), nullable=False), sa.Column("metadata_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"))
    op.create_index("ix_reports_project_id", "reports", ["project_id"])
    op.create_table("activities", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("project_id", sa.Uuid(), nullable=False), sa.Column("actor_name", sa.String(120), nullable=False), sa.Column("action", sa.String(180), nullable=False), sa.Column("category", sa.String(40), nullable=False), sa.Column("details", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"))
    op.create_index("ix_activities_project_id", "activities", ["project_id"])
    op.create_table("milestones", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("project_id", sa.Uuid(), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("status", sa.String(30), nullable=False, server_default="planned"), sa.Column("progress", sa.Integer(), nullable=False, server_default="0"), sa.Column("due_label", sa.String(80), nullable=False, server_default="Next sprint"), sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"))
    op.create_index("ix_milestones_project_id", "milestones", ["project_id"])
    op.create_table("project_risks", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("project_id", sa.Uuid(), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("severity", sa.String(20), nullable=False, server_default="medium"), sa.Column("status", sa.String(30), nullable=False, server_default="open"), sa.Column("owner_name", sa.String(120), nullable=False, server_default="Unassigned"), sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"))
    op.create_index("ix_project_risks_project_id", "project_risks", ["project_id"])


def downgrade() -> None:
    for index, table in (("ix_project_risks_project_id", "project_risks"), ("ix_milestones_project_id", "milestones"), ("ix_activities_project_id", "activities"), ("ix_reports_project_id", "reports"), ("ix_project_memberships_project_id", "project_memberships")):
        op.drop_index(index, table_name=table)
    for table in ("project_risks", "milestones", "activities", "reports", "project_memberships", "people", "project_workspace_metadata"):
        op.drop_table(table)

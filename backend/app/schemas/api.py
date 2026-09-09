from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


Priority = Literal["low", "medium", "high", "critical"]
TaskStatus = Literal["todo", "in_progress", "done", "blocked"]


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=20, max_length=10000)
    target_users: list[str] = Field(default_factory=list, max_length=20)
    preferred_stack: list[str] = Field(default_factory=list, max_length=30)
    team_size: int | None = Field(default=None, ge=1, le=100)

    @field_validator("name", "description")
    @classmethod
    def no_control_chars(cls, value: str) -> str:
        if any(ord(c) < 32 and c not in "\n\t" for c in value):
            raise ValueError("control characters are not allowed")
        return value.strip()


class ProjectSummary(APIModel):
    id: UUID
    name: str
    description: str
    status: str
    team_size: int | None
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectSummary):
    target_users: list[str]
    preferred_stack: list[str]
    requirement_count: int = 0
    component_count: int = 0
    entity_count: int = 0
    task_count: int = 0
    role_count: int = 0
    document_count: int = 0
    generation_status: str | None = None
    objective: str = ""
    actors: list[str] = []
    assumptions: list[str] = []
    constraints: list[str] = []
    risks: list[str] = []
    open_questions: list[str] = []


class RequirementOut(APIModel):
    id: UUID
    project_id: UUID
    category: str
    title: str
    description: str
    priority: str
    source: str


class ArchitectureOut(APIModel):
    id: UUID
    project_id: UUID
    style: str
    rationale: str
    components_json: list
    technologies_json: list
    communication_paths: list
    deployment_concept: str
    scalability_considerations: list


class DatabaseFieldOut(APIModel):
    id: UUID
    entity_id: UUID
    name: str
    data_type: str
    nullable: bool
    primary_key: bool
    unique: bool
    default_value: str | None
    foreign_key: str | None


class DatabaseEntityOut(APIModel):
    id: UUID
    project_id: UUID
    name: str
    description: str
    fields: list[DatabaseFieldOut] = []


class TeamRoleOut(APIModel):
    id: UUID
    project_id: UUID
    name: str
    description: str
    task_count: int = 0
    assigned_task_titles: list[str] = []


class TaskOut(APIModel):
    id: UUID
    project_id: UUID
    parent_id: UUID | None
    task_key: str
    title: str
    description: str
    task_type: str
    priority: str
    status: str
    effort: int
    acceptance_criteria: list
    role_id: UUID | None
    role_name: str | None = None
    dependency_ids: list[UUID] = []


class DocumentOut(APIModel):
    id: UUID
    project_id: UUID
    document_type: str
    content: str
    version: int
    created_at: datetime


class GenerationRunOut(APIModel):
    id: UUID
    project_id: UUID
    run_type: str
    status: str
    current_stage: str | None
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None


class AnalyzeOut(BaseModel):
    run_id: UUID
    status: str
    message: str

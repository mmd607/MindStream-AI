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
    domain: str = Field(default="Software", max_length=80)
    objective: str = Field(default="", max_length=2000)
    constraints: list[str] = Field(default_factory=list, max_length=20)
    important_risks: list[str] = Field(default_factory=list, max_length=20)
    expected_timeline: str = Field(default="12 weeks", max_length=120)
    owner_name: str = Field(default="Alex Morgan", max_length=120)

    @field_validator("name", "description")
    @classmethod
    def no_control_chars(cls, value: str) -> str:
        if any(ord(c) < 32 and c not in "\n\t" for c in value):
            raise ValueError("control characters are not allowed")
        return value.strip()


class ProjectStatusUpdate(BaseModel):
    status: Literal["draft", "planning", "active", "at_risk", "paused", "completed", "archived"]
    reason: str = Field(default="", max_length=1000)


class ProjectSummary(APIModel):
    id: UUID
    name: str
    description: str
    status: str
    team_size: int | None
    created_at: datetime
    updated_at: datetime
    domain: str = "Software"
    status_label: str = "Draft"
    status_reason: str = ""
    health_score: int = 0
    progress: int = 0
    team_member_count: int = 0
    task_count: int = 0
    report_count: int = 0
    feature_count: int = 0
    api_count: int = 0


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
    executive_summary: str = ""
    expected_timeline: str = "12 weeks"
    feature_count: int = 0
    api_count: int = 0


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
    owner_name: str | None = None
    module_name: str | None = None
    feature_name: str | None = None
    assignee_id: UUID | None = None


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


class PersonOut(APIModel):
    id: UUID
    name: str
    email: str
    title: str
    avatar: str | None = None
    project_count: int = 0
    active_task_count: int = 0
    completed_task_count: int = 0
    projects: list[dict] = []


class ProjectMemberOut(APIModel):
    id: UUID
    person_id: UUID
    name: str
    email: str
    title: str
    role_title: str
    workload_percent: int
    modules: list[str] = []
    assigned_task_count: int = 0
    completed_task_count: int = 0


class ReportOut(APIModel):
    id: UUID
    project_id: UUID
    report_type: str
    title: str
    summary: str
    generated_at: datetime
    generated_by: str
    status: str
    score: int | None
    content: str
    metadata_json: dict = {}
    project_name: str | None = None


class ReportUpdate(BaseModel):
    status: Literal["generated", "archived"]


class ActivityOut(APIModel):
    id: UUID
    project_id: UUID
    actor_name: str
    action: str
    category: str
    details: str
    entity_type: str | None = None
    entity_id: UUID | None = None
    created_at: datetime


class MilestoneOut(APIModel):
    id: UUID
    project_id: UUID
    title: str
    description: str
    status: str
    progress: int
    due_label: str
    owner_name: str
    related_task_keys: list = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RiskOut(APIModel):
    id: UUID
    project_id: UUID
    title: str
    description: str
    severity: str
    probability: str
    status: str
    owner_name: str
    mitigation: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FeatureOut(APIModel):
    id: UUID
    project_id: UUID
    requirement_id: UUID | None
    name: str
    description: str
    module_name: str
    status: str
    task_key: str | None


class APIOut(APIModel):
    id: UUID
    project_id: UUID
    method: str
    path: str
    module: str
    purpose: str
    request_schema: str
    response_schema: str
    owner_name: str
    feature_name: str | None
    task_key: str | None
    status: str


class TraceabilityLink(BaseModel):
    requirement_id: UUID
    requirement_title: str
    feature_id: UUID | None
    feature_name: str | None
    module_name: str | None
    api_id: UUID | None
    api_path: str | None
    task_key: str | None
    task_title: str | None
    owner_name: str | None
    coverage: str


class ProjectComparison(BaseModel):
    id: UUID
    name: str
    status: str
    health_score: int
    progress: int
    requirements: int
    features: int
    modules: int
    apis: int
    tasks: int
    team: int
    risks: int


class SearchItem(BaseModel):
    id: UUID
    title: str
    subtitle: str = ""
    kind: str
    project_id: UUID | None = None


class SearchOut(BaseModel):
    query: str
    groups: dict[str, list[SearchItem]]


class InsightOut(BaseModel):
    kind: str
    title: str
    body: str
    severity: str = "info"


class WorkspaceOut(BaseModel):
    projects: list[ProjectSummary]
    people: list[PersonOut]
    recent_activity: list[ActivityOut]
    metrics: dict[str, int]

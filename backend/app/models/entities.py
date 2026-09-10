from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Project(TimestampMixin, Base):
    __tablename__ = "projects"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_users: Mapped[list] = mapped_column(JSON, default=list)
    preferred_stack: Mapped[list] = mapped_column(JSON, default=list)
    team_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    objective: Mapped[str] = mapped_column(Text, default="")
    actors: Mapped[list] = mapped_column(JSON, default=list)
    assumptions: Mapped[list] = mapped_column(JSON, default=list)
    constraints: Mapped[list] = mapped_column(JSON, default=list)
    risks: Mapped[list] = mapped_column(JSON, default=list)
    open_questions: Mapped[list] = mapped_column(JSON, default=list)
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    architecture: Mapped["ArchitecturePlan | None"] = relationship(back_populates="project", cascade="all, delete-orphan", uselist=False)
    entities: Mapped[list["DatabaseEntity"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    roles: Mapped[list["TeamRole"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    generation_runs: Mapped[list["GenerationRun"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    workspace_metadata: Mapped["ProjectWorkspaceMetadata | None"] = relationship(back_populates="project", cascade="all, delete-orphan", uselist=False)
    memberships: Mapped[list["ProjectMembership"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    milestones: Mapped[list["Milestone"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    project_risks: Mapped[list["ProjectRisk"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    features: Mapped[list["ProjectFeature"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    apis: Mapped[list["ProjectAPI"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectWorkspaceMetadata(Base):
    __tablename__ = "project_workspace_metadata"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(80), default="Software", nullable=False)
    status_reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status_description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    expected_timeline: Mapped[str] = mapped_column(String(120), default="12 weeks", nullable=False)
    health_score: Mapped[int] = mapped_column(Integer, default=78, nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    project: Mapped[Project] = relationship(back_populates="workspace_metadata")


class Person(TimestampMixin, Base):
    __tablename__ = "people"
    __table_args__ = (UniqueConstraint("email"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), nullable=False)
    title: Mapped[str] = mapped_column(String(120), default="Project contributor", nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(30), nullable=True)
    memberships: Mapped[list["ProjectMembership"]] = relationship(back_populates="person", cascade="all, delete-orphan")
    task_assignments: Mapped[list["TaskAssignment"]] = relationship(back_populates="person", cascade="all, delete-orphan")


class ProjectMembership(Base):
    __tablename__ = "project_memberships"
    __table_args__ = (Index("ix_project_memberships_project_id", "project_id"), UniqueConstraint("project_id", "person_id"))
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    person_id: Mapped[UUID] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    role_title: Mapped[str] = mapped_column(String(100), nullable=False)
    workload_percent: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    modules_json: Mapped[list] = mapped_column(JSON, default=list)
    project: Mapped[Project] = relationship(back_populates="memberships")
    person: Mapped[Person] = relationship(back_populates="memberships")


class Report(TimestampMixin, Base):
    __tablename__ = "reports"
    __table_args__ = (Index("ix_reports_project_id", "project_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    generated_by: Mapped[str] = mapped_column(String(40), default="mock-ai", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="generated", nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    project: Mapped[Project] = relationship(back_populates="reports")


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (Index("ix_activities_project_id", "project_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    actor_name: Mapped[str] = mapped_column(String(120), default="MindStream AI", nullable=False)
    action: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str] = mapped_column(String(40), default="project", nullable=False)
    details: Mapped[str] = mapped_column(Text, default="", nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    entity_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    project: Mapped[Project] = relationship(back_populates="activities")


class Milestone(TimestampMixin, Base):
    __tablename__ = "milestones"
    __table_args__ = (Index("ix_milestones_project_id", "project_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="planned", nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    due_label: Mapped[str] = mapped_column(String(80), default="Next sprint", nullable=False)
    owner_name: Mapped[str] = mapped_column(String(120), default="Unassigned", nullable=False)
    related_task_keys: Mapped[list] = mapped_column(JSON, default=list)
    project: Mapped[Project] = relationship(back_populates="milestones")


class ProjectRisk(TimestampMixin, Base):
    __tablename__ = "project_risks"
    __table_args__ = (Index("ix_project_risks_project_id", "project_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    probability: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)
    owner_name: Mapped[str] = mapped_column(String(120), default="Unassigned", nullable=False)
    mitigation: Mapped[str] = mapped_column(Text, default="Review mitigation at the next project checkpoint.", nullable=False)
    project: Mapped[Project] = relationship(back_populates="project_risks")


class ProjectFeature(Base):
    __tablename__ = "project_features"
    __table_args__ = (Index("ix_project_features_project_id", "project_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    requirement_id: Mapped[UUID | None] = mapped_column(ForeignKey("requirements.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    module_name: Mapped[str] = mapped_column(String(120), default="Core platform", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="planned", nullable=False)
    task_key: Mapped[str | None] = mapped_column(String(20), nullable=True)
    project: Mapped[Project] = relationship(back_populates="features")
    requirement: Mapped["Requirement | None"] = relationship()


class ProjectAPI(Base):
    __tablename__ = "project_apis"
    __table_args__ = (Index("ix_project_apis_project_id", "project_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(180), nullable=False)
    module: Mapped[str] = mapped_column(String(120), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, default="", nullable=False)
    request_schema: Mapped[str] = mapped_column(Text, default="JSON", nullable=False)
    response_schema: Mapped[str] = mapped_column(Text, default="JSON", nullable=False)
    owner_name: Mapped[str] = mapped_column(String(120), default="Unassigned", nullable=False)
    feature_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    task_key: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="specified", nullable=False)
    project: Mapped[Project] = relationship(back_populates="apis")


class Requirement(Base):
    __tablename__ = "requirements"
    __table_args__ = (Index("ix_requirements_project_id", "project_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    source: Mapped[str] = mapped_column(String(30), default="mock-provider")
    project: Mapped[Project] = relationship(back_populates="requirements")


class ArchitecturePlan(TimestampMixin, Base):
    __tablename__ = "architecture_plans"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)
    style: Mapped[str] = mapped_column(String(100), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    components_json: Mapped[list] = mapped_column(JSON, default=list)
    technologies_json: Mapped[list] = mapped_column(JSON, default=list)
    communication_paths: Mapped[list] = mapped_column(JSON, default=list)
    deployment_concept: Mapped[str] = mapped_column(Text, default="")
    scalability_considerations: Mapped[list] = mapped_column(JSON, default=list)
    project: Mapped[Project] = relationship(back_populates="architecture")


class DatabaseEntity(Base):
    __tablename__ = "database_entities"
    __table_args__ = (Index("ix_database_entities_project_id", "project_id"), UniqueConstraint("project_id", "name"))
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    project: Mapped[Project] = relationship(back_populates="entities")
    fields: Mapped[list["DatabaseField"]] = relationship(back_populates="entity", cascade="all, delete-orphan")


class DatabaseField(Base):
    __tablename__ = "database_fields"
    __table_args__ = (Index("ix_database_fields_entity_id", "entity_id"), UniqueConstraint("entity_id", "name"))
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    entity_id: Mapped[UUID] = mapped_column(ForeignKey("database_entities.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)
    nullable: Mapped[bool] = mapped_column(Boolean, default=True)
    primary_key: Mapped[bool] = mapped_column(Boolean, default=False)
    unique: Mapped[bool] = mapped_column(Boolean, default=False)
    default_value: Mapped[str | None] = mapped_column(String(120), nullable=True)
    foreign_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    entity: Mapped[DatabaseEntity] = relationship(back_populates="fields")


class TeamRole(Base):
    __tablename__ = "team_roles"
    __table_args__ = (Index("ix_team_roles_project_id", "project_id"), UniqueConstraint("project_id", "name"))
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    project: Mapped[Project] = relationship(back_populates="roles")
    tasks: Mapped[list["Task"]] = relationship(back_populates="role")


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (Index("ix_tasks_project_id", "project_id"), Index("ix_tasks_role_id", "role_id"))
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    task_key: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    task_type: Mapped[str] = mapped_column(String(30), default="task")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(30), default="todo")
    effort: Mapped[int] = mapped_column(Integer, default=1)
    acceptance_criteria: Mapped[list] = mapped_column(JSON, default=list)
    role_id: Mapped[UUID | None] = mapped_column(ForeignKey("team_roles.id", ondelete="SET NULL"), nullable=True)
    project: Mapped[Project] = relationship(back_populates="tasks")
    role: Mapped[TeamRole | None] = relationship(back_populates="tasks")
    parent: Mapped["Task | None"] = relationship(remote_side=[id])
    assignments: Mapped[list["TaskAssignment"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class TaskAssignment(Base):
    __tablename__ = "task_assignments"
    __table_args__ = (Index("ix_task_assignments_task_id", "task_id"), UniqueConstraint("task_id", "person_id"))
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    person_id: Mapped[UUID] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    task: Mapped[Task] = relationship(back_populates="assignments")
    person: Mapped[Person] = relationship(back_populates="task_assignments")


class Dependency(Base):
    __tablename__ = "dependencies"
    __table_args__ = (Index("ix_dependencies_task_id", "task_id"), UniqueConstraint("task_id", "depends_on_task_id"))
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    depends_on_task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (Index("ix_documents_project_id", "project_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(40), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    project: Mapped[Project] = relationship(back_populates="documents")


class GenerationRun(Base):
    __tablename__ = "generation_runs"
    __table_args__ = (Index("ix_generation_runs_project_id", "project_id"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    run_type: Mapped[str] = mapped_column(String(40), default="full")
    status: Mapped[str] = mapped_column(String(30), default="queued")
    current_stage: Mapped[str | None] = mapped_column(String(40), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    project: Mapped[Project] = relationship(back_populates="generation_runs")

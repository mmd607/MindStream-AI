from pydantic import BaseModel, Field


class RequirementPlan(BaseModel):
    category: str
    title: str = Field(min_length=3)
    description: str = Field(min_length=5)
    priority: str = "medium"


class ComponentPlan(BaseModel):
    name: str
    responsibility: str


class TechnologyPlan(BaseModel):
    name: str
    rationale: str


class EntityFieldPlan(BaseModel):
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default_value: str | None = None
    foreign_key: str | None = None


class EntityPlan(BaseModel):
    name: str
    description: str
    fields: list[EntityFieldPlan] = Field(min_length=1)


class RolePlan(BaseModel):
    name: str
    description: str


class TaskPlan(BaseModel):
    key: str
    title: str
    description: str
    task_type: str = "task"
    priority: str = "medium"
    effort: int = Field(default=1, ge=1, le=100)
    role: str
    depends_on: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(min_length=1)


class Blueprint(BaseModel):
    objective: str
    actors: list[str]
    functional_requirements: list[RequirementPlan]
    non_functional_requirements: list[RequirementPlan]
    assumptions: list[str]
    constraints: list[str]
    risks: list[str]
    open_questions: list[str]
    architecture_style: str
    architecture_rationale: str
    components: list[ComponentPlan]
    technologies: list[TechnologyPlan]
    communication_paths: list[str]
    deployment_concept: str
    scalability_considerations: list[str]
    entities: list[EntityPlan]
    roles: list[RolePlan]
    tasks: list[TaskPlan]
    api_modules: list[str]

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.ai.factory import get_provider
from app.ai.schemas import Blueprint
from app.models import ArchitecturePlan, DatabaseEntity, DatabaseField, Dependency, Document, GenerationRun, Project, ProjectAPI, ProjectFeature, Requirement, Task, TeamRole
from app.planners.documentation import markdown_for_blueprint
from app.planners.validator import validate_blueprint


STAGES = ["analyzing", "planning_architecture", "planning_database", "planning_api", "planning_tasks", "validating", "generating_docs"]


class PlanningOrchestrator:
    def run(self, db: Session, project: Project, run: GenerationRun) -> Blueprint:
        provider = get_provider()
        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        db.flush()
        blueprint = provider.generate_blueprint(project.name, project.description, project.preferred_stack)
        for stage in STAGES:
            run.current_stage = stage
            db.flush()
        errors = validate_blueprint(blueprint)
        if errors:
            raise ValueError("Generated plan failed consistency validation: " + "; ".join(errors))
        self._persist(db, project, blueprint, provider.name)
        run.current_stage = None
        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        project.status = "completed"
        db.flush()
        return blueprint

    def _persist(self, db: Session, project: Project, blueprint: Blueprint, source: str) -> None:
        project.objective = blueprint.objective
        project.actors = blueprint.actors
        project.assumptions = blueprint.assumptions
        project.constraints = blueprint.constraints
        project.risks = blueprint.risks
        project.open_questions = blueprint.open_questions
        task_ids = list(db.scalars(select(Task.id).where(Task.project_id == project.id)).all())
        if task_ids:
            db.execute(delete(Dependency).where((Dependency.task_id.in_(task_ids)) | (Dependency.depends_on_task_id.in_(task_ids))))
        for model in (Requirement, ArchitecturePlan, DatabaseEntity, TeamRole, Task, Document, ProjectFeature, ProjectAPI):
            db.execute(delete(model).where(model.project_id == project.id))
        db.flush()
        requirement_records = []
        for item in blueprint.functional_requirements + blueprint.non_functional_requirements:
            record = Requirement(project_id=project.id, category=item.category, title=item.title, description=item.description, priority=item.priority, source=source)
            db.add(record)
            requirement_records.append(record)
        db.add(ArchitecturePlan(project_id=project.id, style=blueprint.architecture_style, rationale=blueprint.architecture_rationale, components_json=[item.model_dump() for item in blueprint.components], technologies_json=[item.model_dump() for item in blueprint.technologies], communication_paths=blueprint.communication_paths, deployment_concept=blueprint.deployment_concept, scalability_considerations=blueprint.scalability_considerations))
        for entity in blueprint.entities:
            record = DatabaseEntity(project_id=project.id, name=entity.name, description=entity.description)
            record.fields = [DatabaseField(name=field.name, data_type=field.data_type, nullable=field.nullable, primary_key=field.primary_key, unique=field.unique, default_value=field.default_value, foreign_key=field.foreign_key) for field in entity.fields]
            db.add(record)
        roles = {role.name: TeamRole(project_id=project.id, name=role.name, description=role.description) for role in blueprint.roles}
        for role in roles.values():
            db.add(role)
        db.flush()
        task_records: dict[str, Task] = {}
        for item in blueprint.tasks:
            record = Task(project_id=project.id, task_key=item.key, title=item.title, description=item.description, task_type=item.task_type, priority=item.priority, effort=item.effort, acceptance_criteria=item.acceptance_criteria, role_id=roles[item.role].id)
            db.add(record)
            task_records[item.key] = record
        db.flush()
        for item in blueprint.tasks:
            for dependency in item.depends_on:
                db.add(Dependency(task_id=task_records[item.key].id, depends_on_task_id=task_records[dependency].id))
        db.flush()
        components = [item.name for item in blueprint.components] or ["Core platform"]
        for index, requirement in enumerate(requirement_records):
            feature = ProjectFeature(project_id=project.id, requirement_id=requirement.id, name=f"{requirement.title} workflow", description=requirement.description, module_name=components[index % len(components)], status="planned", task_key=blueprint.tasks[index % len(blueprint.tasks)].key if blueprint.tasks else None)
            db.add(feature)
        for index, module in enumerate(blueprint.api_modules):
            task = blueprint.tasks[index % len(blueprint.tasks)] if blueprint.tasks else None
            db.add(ProjectAPI(project_id=project.id, method=["GET", "POST", "PATCH"][index % 3], path=f"/api/v1/{module.lower().replace(' ', '-')}", module=module, purpose=f"Support {module.lower()} workflows for the project.", request_schema="JSON", response_schema="JSON", owner_name=task.role if task else "Unassigned", feature_name=f"{requirement_records[index % len(requirement_records)].title} workflow" if requirement_records else None, task_key=task.key if task else None, status="specified"))
        markdown = markdown_for_blueprint(project.name, project.description, blueprint)
        db.add(Document(project_id=project.id, document_type="project_blueprint", content=markdown, version=1))

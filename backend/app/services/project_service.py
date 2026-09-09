from __future__ import annotations

import json
import re
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import ArchitecturePlan, DatabaseEntity, Document, GenerationRun, Project, Requirement, Task, TeamRole
from app.schemas.api import ArchitectureOut, DatabaseEntityOut, DocumentOut, GenerationRunOut, ProjectDetail, ProjectSummary, RequirementOut, TaskOut, TeamRoleOut


class ProjectService:
    def create(self, db: Session, data) -> ProjectSummary:
        project = Project(**data.model_dump(), status="draft")
        db.add(project)
        db.commit()
        db.refresh(project)
        return ProjectSummary.model_validate(project)

    def list(self, db: Session) -> list[ProjectSummary]:
        return [ProjectSummary.model_validate(item) for item in db.scalars(select(Project).order_by(Project.created_at.desc())).all()]

    def get(self, db: Session, project_id: UUID) -> Project:
        project = db.scalar(select(Project).where(Project.id == project_id))
        if not project:
            raise HTTPException(status_code=404, detail={"code": "project_not_found", "message": "Project not found"})
        return project

    def detail(self, db: Session, project_id: UUID) -> ProjectDetail:
        project = self.get(db, project_id)
        latest_run = db.scalar(select(GenerationRun).where(GenerationRun.project_id == project.id).order_by(GenerationRun.started_at.desc()))
        architecture = db.scalar(select(ArchitecturePlan).where(ArchitecturePlan.project_id == project.id))
        return ProjectDetail.model_validate({**ProjectSummary.model_validate(project).model_dump(), "target_users": project.target_users, "preferred_stack": project.preferred_stack, "requirement_count": len(project.requirements), "component_count": len(architecture.components_json) if architecture else 0, "entity_count": len(project.entities), "task_count": len(project.tasks), "role_count": len(project.roles), "document_count": len(project.documents), "generation_status": latest_run.status if latest_run else None, "objective": project.objective, "actors": project.actors, "assumptions": project.assumptions, "constraints": project.constraints, "risks": project.risks, "open_questions": project.open_questions})

    def delete(self, db: Session, project_id: UUID) -> None:
        project = self.get(db, project_id)
        db.delete(project)
        db.commit()

    def requirements(self, db: Session, project_id: UUID) -> list[RequirementOut]:
        self.get(db, project_id)
        return [RequirementOut.model_validate(x) for x in db.scalars(select(Requirement).where(Requirement.project_id == project_id).order_by(Requirement.category, Requirement.id)).all()]

    def architecture(self, db: Session, project_id: UUID) -> ArchitectureOut | None:
        self.get(db, project_id)
        item = db.scalar(select(ArchitecturePlan).where(ArchitecturePlan.project_id == project_id))
        return ArchitectureOut.model_validate(item) if item else None

    def database(self, db: Session, project_id: UUID) -> list[DatabaseEntityOut]:
        self.get(db, project_id)
        items = db.scalars(select(DatabaseEntity).options(selectinload(DatabaseEntity.fields)).where(DatabaseEntity.project_id == project_id).order_by(DatabaseEntity.name)).all()
        return [DatabaseEntityOut.model_validate(item) for item in items]

    def tasks(self, db: Session, project_id: UUID) -> list[TaskOut]:
        self.get(db, project_id)
        items = db.scalars(select(Task).options(selectinload(Task.role)).where(Task.project_id == project_id).order_by(Task.id)).all()
        ids = [item.id for item in items]
        from app.models.entities import Dependency
        dependencies = db.scalars(select(Dependency).where(Dependency.task_id.in_(ids))).all() if ids else []
        by_task: dict[UUID, list[UUID]] = {}
        for item in dependencies:
            by_task.setdefault(item.task_id, []).append(item.depends_on_task_id)
        return [TaskOut.model_validate({**TaskOut.model_validate(item).model_dump(), "role_name": item.role.name if item.role else None, "dependency_ids": by_task.get(item.id, [])}) for item in items]

    def roles(self, db: Session, project_id: UUID) -> list[TeamRoleOut]:
        self.get(db, project_id)
        roles = db.scalars(select(TeamRole).options(selectinload(TeamRole.tasks)).where(TeamRole.project_id == project_id).order_by(TeamRole.name)).all()
        return [TeamRoleOut.model_validate({**TeamRoleOut.model_validate(x).model_dump(), "task_count": len(x.tasks), "assigned_task_titles": [task.title for task in x.tasks]}) for x in roles]

    def documents(self, db: Session, project_id: UUID) -> list[DocumentOut]:
        self.get(db, project_id)
        return [DocumentOut.model_validate(x) for x in db.scalars(select(Document).where(Document.project_id == project_id).order_by(Document.document_type)).all()]

    def runs(self, db: Session, project_id: UUID) -> list[GenerationRunOut]:
        self.get(db, project_id)
        return [GenerationRunOut.model_validate(x) for x in db.scalars(select(GenerationRun).where(GenerationRun.project_id == project_id).order_by(GenerationRun.started_at.desc())).all()]

    def export(self, db: Session, project_id: UUID, format_name: str) -> tuple[str, str, str]:
        project = self.get(db, project_id)
        requirements = self.requirements(db, project_id)
        architecture = self.architecture(db, project_id)
        database = self.database(db, project_id)
        tasks = self.tasks(db, project_id)
        roles = self.roles(db, project_id)
        documents = self.documents(db, project_id)
        data = {"project": ProjectDetail.model_validate(self.detail(db, project_id)).model_dump(mode="json"), "requirements": [item.model_dump(mode="json") for item in requirements], "architecture": architecture.model_dump(mode="json") if architecture else None, "database": [item.model_dump(mode="json") for item in database], "tasks": [item.model_dump(mode="json") for item in tasks], "roles": [item.model_dump(mode="json") for item in roles], "documents": [item.model_dump(mode="json") for item in documents]}
        safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "-", project.name).strip("-")[:60] or "project"
        if format_name == "json":
            return json.dumps(data, indent=2), "application/json", safe_name + ".json"
        if format_name == "markdown":
            content = documents[0].content if documents else f"# {project.name}\n\n{project.description}\n"
            return content, "text/markdown; charset=utf-8", safe_name + ".md"
        raise HTTPException(status_code=400, detail={"code": "invalid_export_format", "message": "format must be markdown or json"})

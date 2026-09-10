from __future__ import annotations

import json
import re
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Activity, ArchitecturePlan, DatabaseEntity, Document, GenerationRun, Milestone,
    Person, Project, ProjectAPI, ProjectFeature, ProjectMembership, ProjectRisk, ProjectWorkspaceMetadata, Report,
    Requirement, Task, TeamRole,
)
from app.schemas.api import (
    ActivityOut, ArchitectureOut, DatabaseEntityOut, DocumentOut, GenerationRunOut,
    MilestoneOut, PersonOut, ProjectCreate, ProjectDetail, ProjectMemberOut,
    ProjectSummary, ReportOut, RequirementOut, RiskOut, TaskOut, TeamRoleOut, APIOut, FeatureOut, TraceabilityLink, ProjectComparison, SearchItem, InsightOut,
)


STATUS_LABELS = {"draft": "Draft", "planning": "Planning", "active": "Active", "at_risk": "At risk", "paused": "Paused", "completed": "Completed", "archived": "Archived"}


class ProjectService:
    def create(self, db: Session, data: ProjectCreate) -> ProjectSummary:
        project = Project(name=data.name, description=data.description, target_users=data.target_users, preferred_stack=data.preferred_stack, team_size=data.team_size, status="draft", objective=data.objective, constraints=data.constraints, risks=data.important_risks)
        db.add(project)
        db.flush()
        db.add(ProjectWorkspaceMetadata(project_id=project.id, domain=data.domain, expected_timeline=data.expected_timeline, status_description="Ready for analysis"))
        owner = self._get_or_create_person(db, data.owner_name, f"{self._slug(data.owner_name)}@example.local", "Project owner")
        db.add(ProjectMembership(project_id=project.id, person_id=owner.id, role_title="Project Manager", workload_percent=40, modules_json=["Scope", "Milestones"]))
        db.add(Activity(project_id=project.id, actor_name=data.owner_name, action="Created project workspace", category="project", details="Project context is ready for blueprint analysis."))
        db.commit()
        db.refresh(project)
        return self._summary(project)

    def list(self, db: Session, search: str = "", status: str = "", domain: str = "") -> list[ProjectSummary]:
        query = select(Project).options(selectinload(Project.workspace_metadata), selectinload(Project.memberships), selectinload(Project.tasks), selectinload(Project.reports), selectinload(Project.features), selectinload(Project.apis)).order_by(Project.created_at.desc())
        if search:
            query = query.where(Project.name.ilike(f"%{search}%"))
        if status:
            query = query.where(Project.status == status)
        projects = db.scalars(query).all()
        if domain:
            projects = [item for item in projects if (item.workspace_metadata.domain if item.workspace_metadata else "Software").lower() == domain.lower()]
        return [self._summary(item) for item in projects]

    def _summary(self, project: Project) -> ProjectSummary:
        metadata = project.workspace_metadata
        return ProjectSummary.model_validate({"id": project.id, "name": project.name, "description": project.description, "status": project.status, "team_size": project.team_size, "created_at": project.created_at, "updated_at": project.updated_at, "domain": metadata.domain if metadata else "Software", "status_label": STATUS_LABELS.get(project.status, project.status.replace("_", " ").title()), "status_reason": metadata.status_reason if metadata else "", "health_score": metadata.health_score if metadata else self._health(project), "progress": metadata.progress if metadata else self._progress(project), "team_member_count": len(project.memberships), "task_count": len(project.tasks), "report_count": len(project.reports), "feature_count": len(project.features), "api_count": len(project.apis)})

    def get(self, db: Session, project_id: UUID) -> Project:
        project = db.scalar(select(Project).options(selectinload(Project.workspace_metadata)).where(Project.id == project_id))
        if not project:
            raise HTTPException(status_code=404, detail={"code": "project_not_found", "message": "Project not found"})
        return project

    def detail(self, db: Session, project_id: UUID) -> ProjectDetail:
        project = self.get(db, project_id)
        latest_run = db.scalar(select(GenerationRun).where(GenerationRun.project_id == project.id).order_by(GenerationRun.started_at.desc()))
        architecture = db.scalar(select(ArchitecturePlan).where(ArchitecturePlan.project_id == project.id))
        metadata = project.workspace_metadata
        summary = self._summary(project).model_dump()
        return ProjectDetail.model_validate({**summary, "target_users": project.target_users or [], "preferred_stack": project.preferred_stack or [], "requirement_count": len(project.requirements), "component_count": len(architecture.components_json) if architecture else 0, "entity_count": len(project.entities), "task_count": len(project.tasks), "role_count": len(project.roles), "document_count": len(project.documents), "generation_status": latest_run.status if latest_run else None, "objective": project.objective or "", "actors": project.actors or [], "assumptions": project.assumptions or [], "constraints": project.constraints or [], "risks": project.risks or [], "open_questions": project.open_questions or [], "executive_summary": metadata.executive_summary if metadata else "", "expected_timeline": metadata.expected_timeline if metadata else "12 weeks"})

    def delete(self, db: Session, project_id: UUID) -> None:
        project = self.get(db, project_id)
        db.delete(project)
        db.commit()

    def update_status(self, db: Session, project_id: UUID, status: str, reason: str) -> ProjectSummary:
        project = self.get(db, project_id)
        project.status = status
        metadata = project.workspace_metadata or ProjectWorkspaceMetadata(project_id=project.id)
        metadata.status_reason = reason
        metadata.status_description = f"Status updated to {STATUS_LABELS.get(status, status)}"
        db.add(metadata)
        db.add(Activity(project_id=project.id, actor_name="Workspace user", action=f"Moved project to {STATUS_LABELS.get(status, status)}", category="project", details=reason or "Status updated from the project dashboard."))
        db.commit()
        db.refresh(project)
        return self._summary(project)

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
        items = db.scalars(select(Task).options(selectinload(Task.role)).where(Task.project_id == project_id).order_by(Task.task_key, Task.id)).all()
        ids = [item.id for item in items]
        from app.models.entities import Dependency
        dependencies = db.scalars(select(Dependency).where(Dependency.task_id.in_(ids))).all() if ids else []
        by_task: dict[UUID, list[UUID]] = {}
        for item in dependencies:
            by_task.setdefault(item.task_id, []).append(item.depends_on_task_id)
        features = db.scalars(select(ProjectFeature).where(ProjectFeature.project_id == project_id)).all()
        feature_by_key = {item.task_key: item for item in features if item.task_key}
        memberships = db.scalars(select(ProjectMembership).options(selectinload(ProjectMembership.person)).where(ProjectMembership.project_id == project_id)).all()
        owners = {item.role_title: item.person.name for item in memberships}
        fallback_owner = memberships[0].person.name if memberships else None
        return [TaskOut.model_validate({**TaskOut.model_validate(item).model_dump(), "role_name": item.role.name if item.role else None, "dependency_ids": by_task.get(item.id, []), "owner_name": owners.get(item.role.name, fallback_owner) if item.role else fallback_owner, "module_name": feature_by_key.get(item.task_key).module_name if item.task_key in feature_by_key else None, "feature_name": feature_by_key.get(item.task_key).name if item.task_key in feature_by_key else None}) for item in items]

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

    def features(self, db: Session, project_id: UUID) -> list[FeatureOut]:
        self.get(db, project_id)
        return [FeatureOut.model_validate(item) for item in db.scalars(select(ProjectFeature).where(ProjectFeature.project_id == project_id).order_by(ProjectFeature.name)).all()]

    def apis(self, db: Session, project_id: UUID, search: str = "", method: str = "", module: str = "") -> list[APIOut]:
        self.get(db, project_id)
        query = select(ProjectAPI).where(ProjectAPI.project_id == project_id).order_by(ProjectAPI.path)
        if method:
            query = query.where(ProjectAPI.method == method.upper())
        if module:
            query = query.where(ProjectAPI.module == module)
        items = db.scalars(query).all()
        if search:
            term = search.lower()
            items = [item for item in items if term in f"{item.path} {item.purpose} {item.module}".lower()]
        return [APIOut.model_validate(item) for item in items]

    def traceability(self, db: Session, project_id: UUID) -> list[TraceabilityLink]:
        project = self.get(db, project_id)
        requirements = db.scalars(select(Requirement).where(Requirement.project_id == project_id).order_by(Requirement.id)).all()
        features = db.scalars(select(ProjectFeature).where(ProjectFeature.project_id == project_id)).all()
        apis = db.scalars(select(ProjectAPI).where(ProjectAPI.project_id == project_id)).all()
        tasks = db.scalars(select(Task).options(selectinload(Task.role)).where(Task.project_id == project_id)).all()
        memberships = db.scalars(select(ProjectMembership).options(selectinload(ProjectMembership.person)).where(ProjectMembership.project_id == project_id)).all()
        feature_by_requirement = {item.requirement_id: item for item in features}
        api_by_feature = {item.feature_name: item for item in apis}
        role_owners = {item.role_title: item.person.name for item in memberships}
        task_by_key = {item.task_key: item for item in tasks}
        result = []
        for requirement in requirements:
            feature = feature_by_requirement.get(requirement.id)
            api = api_by_feature.get(feature.name) if feature else None
            task = task_by_key.get(feature.task_key) if feature and feature.task_key else None
            owner = role_owners.get(task.role.name, memberships[0].person.name if memberships else None) if task and task.role else (memberships[0].person.name if memberships else None)
            covered = bool(feature and task and api)
            result.append(TraceabilityLink.model_validate({"requirement_id": requirement.id, "requirement_title": requirement.title, "feature_id": feature.id if feature else None, "feature_name": feature.name if feature else None, "module_name": feature.module_name if feature else None, "api_id": api.id if api else None, "api_path": api.path if api else None, "task_key": task.task_key if task else (feature.task_key if feature else None), "task_title": task.title if task else None, "owner_name": owner, "coverage": "covered" if covered else "needs attention"}))
        return result

    def compare(self, db: Session, project_ids: list[UUID]) -> list[ProjectComparison]:
        if not project_ids or len(project_ids) > 4:
            raise HTTPException(status_code=400, detail={"code": "invalid_comparison", "message": "Select between 2 and 4 projects to compare"})
        projects = db.scalars(select(Project).options(selectinload(Project.workspace_metadata), selectinload(Project.memberships), selectinload(Project.tasks), selectinload(Project.reports), selectinload(Project.features), selectinload(Project.apis)).where(Project.id.in_(project_ids))).all()
        if len(projects) != len(set(project_ids)):
            raise HTTPException(status_code=404, detail={"code": "project_not_found", "message": "One or more projects were not found"})
        return [ProjectComparison.model_validate({"id": project.id, "name": project.name, "status": project.status, "health_score": project.workspace_metadata.health_score if project.workspace_metadata else self._health(project), "progress": project.workspace_metadata.progress if project.workspace_metadata else self._progress(project), "requirements": len(project.requirements), "features": len(project.features), "modules": len(project.architecture.components_json) if project.architecture else 0, "apis": len(project.apis), "tasks": len(project.tasks), "team": len(project.memberships), "risks": len(project.project_risks)}) for project in projects]

    def update_report(self, db: Session, report_id: UUID, status: str) -> ReportOut:
        item = db.get(Report, report_id)
        if not item:
            raise HTTPException(status_code=404, detail={"code": "report_not_found", "message": "Report not found"})
        item.status = status
        db.add(Activity(project_id=item.project_id, actor_name="Workspace user", action=f"Report {status}", category="report", details=item.title))
        db.commit()
        db.refresh(item)
        return self._report_out(item)

    def search(self, db: Session, query: str):
        term = f"%{query.strip()}%"
        projects = db.scalars(select(Project).where(or_(Project.name.ilike(term), Project.description.ilike(term))).limit(8)).all()
        people = db.scalars(select(Person).where(or_(Person.name.ilike(term), Person.title.ilike(term))).limit(8)).all()
        requirements = db.scalars(select(Requirement).where(or_(Requirement.title.ilike(term), Requirement.description.ilike(term))).limit(8)).all()
        features = db.scalars(select(ProjectFeature).where(or_(ProjectFeature.name.ilike(term), ProjectFeature.module_name.ilike(term))).limit(8)).all()
        apis = db.scalars(select(ProjectAPI).where(or_(ProjectAPI.path.ilike(term), ProjectAPI.module.ilike(term), ProjectAPI.purpose.ilike(term))).limit(8)).all()
        tasks = db.scalars(select(Task).where(or_(Task.title.ilike(term), Task.description.ilike(term))).limit(8)).all()
        reports = db.scalars(select(Report).where(or_(Report.title.ilike(term), Report.summary.ilike(term))).limit(8)).all()
        risks = db.scalars(select(ProjectRisk).where(or_(ProjectRisk.title.ilike(term), ProjectRisk.description.ilike(term))).limit(8)).all()
        return {"query": query, "groups": {"projects": [SearchItem(id=item.id, title=item.name, subtitle=item.description, kind="project") for item in projects], "people": [SearchItem(id=item.id, title=item.name, subtitle=item.title, kind="person") for item in people], "requirements": [SearchItem(id=item.id, title=item.title, subtitle=item.description, kind="requirement", project_id=item.project_id) for item in requirements], "features": [SearchItem(id=item.id, title=item.name, subtitle=item.module_name, kind="feature", project_id=item.project_id) for item in features], "apis": [SearchItem(id=item.id, title=item.path, subtitle=item.module, kind="api", project_id=item.project_id) for item in apis], "tasks": [SearchItem(id=item.id, title=item.title, subtitle=item.task_key, kind="task", project_id=item.project_id) for item in tasks], "reports": [SearchItem(id=item.id, title=item.title, subtitle=item.report_type, kind="report", project_id=item.project_id) for item in reports], "risks": [SearchItem(id=item.id, title=item.title, subtitle=item.severity, kind="risk", project_id=item.project_id) for item in risks]}}

    def insights(self, db: Session, project_id: UUID) -> list[InsightOut]:
        project = self.get(db, project_id)
        architecture = db.scalar(select(ArchitecturePlan).where(ArchitecturePlan.project_id == project_id))
        links = self.traceability(db, project_id)
        tasks = db.scalars(select(Task).where(Task.project_id == project_id)).all()
        risks = db.scalars(select(ProjectRisk).where(ProjectRisk.project_id == project_id)).all()
        covered = round(sum(item.coverage == "covered" for item in links) / len(links) * 100) if links else 0
        blocked = sum(item.status == "blocked" for item in tasks)
        urgent_risks = sum(item.severity in ("high", "critical") and item.status == "open" for item in risks)
        return [InsightOut(kind="architecture", title="Architecture insight", body=f"{architecture.style if architecture else 'The architecture'} has {len(architecture.components_json) if architecture else 0} visible components and a clear path from client to persistence.", severity="info"), InsightOut(kind="delivery", title="Delivery insight", body=f"{blocked} tasks are currently blocked and {sum(item.priority in ('high', 'critical') for item in tasks)} tasks are high priority.", severity="warning" if blocked else "info"), InsightOut(kind="requirements", title="Requirements insight", body=f"{covered}% of requirements are traceable across feature, API, task, and ownership links.", severity="success" if covered >= 80 else "warning"), InsightOut(kind="team", title="Team insight", body=f"{len(project.memberships)} people are connected to this project and can be followed through their cross-project profiles.", severity="info"), InsightOut(kind="risk", title="Risk insight", body=f"{urgent_risks} high-severity open risks need attention before the next checkpoint.", severity="danger" if urgent_risks else "success")]

    def members(self, db: Session, project_id: UUID) -> list[ProjectMemberOut]:
        self.get(db, project_id)
        memberships = db.scalars(select(ProjectMembership).options(selectinload(ProjectMembership.person)).where(ProjectMembership.project_id == project_id).order_by(ProjectMembership.role_title)).all()
        tasks = db.scalars(select(Task).options(selectinload(Task.role)).where(Task.project_id == project_id)).all()
        return [ProjectMemberOut.model_validate({"id": item.id, "person_id": item.person_id, "name": item.person.name, "email": item.person.email, "title": item.person.title, "role_title": item.role_title, "workload_percent": item.workload_percent, "modules": item.modules_json or [], "assigned_task_count": sum(1 for task in tasks if task.role and task.role.name == item.role_title), "completed_task_count": sum(1 for task in tasks if task.role and task.role.name == item.role_title and task.status == "done")}) for item in memberships]

    def people(self, db: Session, search: str = "") -> list[PersonOut]:
        query = select(Person).options(selectinload(Person.memberships).selectinload(ProjectMembership.project)).order_by(Person.name)
        if search:
            query = query.where(Person.name.ilike(f"%{search}%"))
        result = []
        for person in db.scalars(query).all():
            memberships = person.memberships
            project_ids = [item.project_id for item in memberships]
            tasks = db.scalars(select(Task).where(Task.project_id.in_(project_ids))).all() if project_ids else []
            result.append(PersonOut.model_validate({"id": person.id, "name": person.name, "email": person.email, "title": person.title, "avatar": person.avatar, "project_count": len(memberships), "active_task_count": sum(1 for task in tasks if task.status not in ("done", "completed")), "completed_task_count": sum(1 for task in tasks if task.status in ("done", "completed")), "projects": [{"id": item.project.id, "name": item.project.name, "status": item.project.status} for item in memberships]}))
        return result

    def person(self, db: Session, person_id: UUID) -> PersonOut:
        if not db.scalar(select(Person.id).where(Person.id == person_id)):
            raise HTTPException(status_code=404, detail={"code": "person_not_found", "message": "Person not found"})
        return next(item for item in self.people(db) if item.id == person_id)

    def reports(self, db: Session, project_id: UUID) -> list[ReportOut]:
        self.get(db, project_id)
        return [self._report_out(item) for item in db.scalars(select(Report).where(Report.project_id == project_id).order_by(Report.created_at.desc())).all()]

    def report(self, db: Session, report_id: UUID) -> ReportOut:
        item = db.get(Report, report_id)
        if not item:
            raise HTTPException(status_code=404, detail={"code": "report_not_found", "message": "Report not found"})
        return self._report_out(item)

    def generate_report(self, db: Session, project_id: UUID, report_type: str = "health") -> ReportOut:
        project = self.get(db, project_id)
        titles = {"architecture": "Architecture Analysis", "health": "Weekly Project Health", "requirements": "Requirements Coverage", "risk": "Risk Assessment", "team": "Team Workload", "api": "API Coverage", "delivery": "Delivery Report"}
        title = titles.get(report_type, "AI Executive Summary")
        health = project.workspace_metadata.health_score if project.workspace_metadata else self._health(project)
        score = max(1, min(99, health + (4 if report_type == "architecture" else 0)))
        summary = f"{project.name} has {len(project.requirements)} requirements, {len(project.tasks)} delivery tasks and {len(project.memberships)} contributors."
        content = f"# {title}\n\n## AI analysis\n\n{summary}\n\n## Overall score\n\n**{score} / 100**\n\n## Strengths\n\n- Structured project context and clear ownership\n- Deterministic blueprint is available for local review\n- Core delivery dependencies are visible\n\n## Attention needed\n\n- Review open risks before the next milestone\n- Connect uncovered requirements to implementation tasks\n\n## Recommended next step\n\nReview the highest-priority task with its owner and update the project status after the next delivery checkpoint.\n"
        item = Report(project_id=project.id, report_type=report_type, title=title, summary=summary, generated_by="mock-ai", status="generated", score=score, content=content, metadata_json={"requirements": len(project.requirements), "tasks": len(project.tasks), "team": len(project.memberships)})
        db.add(item)
        db.add(Activity(project_id=project.id, actor_name="MindStream AI", action=f"Generated {title}", category="report", details="The report is based on current project intelligence."))
        db.commit()
        db.refresh(item)
        return self._report_out(item)

    def activities(self, db: Session, project_id: UUID) -> list[ActivityOut]:
        self.get(db, project_id)
        return [ActivityOut.model_validate(x) for x in db.scalars(select(Activity).where(Activity.project_id == project_id).order_by(Activity.created_at.desc())).all()]

    def milestones(self, db: Session, project_id: UUID) -> list[MilestoneOut]:
        self.get(db, project_id)
        return [MilestoneOut.model_validate(x) for x in db.scalars(select(Milestone).where(Milestone.project_id == project_id).order_by(Milestone.id)).all()]

    def risks(self, db: Session, project_id: UUID) -> list[RiskOut]:
        self.get(db, project_id)
        return [RiskOut.model_validate(x) for x in db.scalars(select(ProjectRisk).where(ProjectRisk.project_id == project_id).order_by(ProjectRisk.severity, ProjectRisk.id)).all()]

    def workspace(self, db: Session):
        projects = self.list(db)
        people = self.people(db)
        activity = [ActivityOut.model_validate(item) for item in db.scalars(select(Activity).order_by(Activity.created_at.desc()).limit(12)).all()]
        return {"projects": projects, "people": people[:8], "recent_activity": activity, "metrics": {"projects": len(projects), "active_projects": sum(1 for item in projects if item.status in ("active", "planning", "at_risk")), "people": len(people), "reports": db.scalar(select(func.count(Report.id))) or 0}}

    @staticmethod
    def _report_out(item: Report) -> ReportOut:
        return ReportOut.model_validate({"id": item.id, "project_id": item.project_id, "report_type": item.report_type, "title": item.title, "summary": item.summary, "generated_at": item.created_at, "generated_by": item.generated_by, "status": item.status, "score": item.score, "content": item.content, "metadata_json": item.metadata_json or {}})

    def export(self, db: Session, project_id: UUID, format_name: str) -> tuple[str, str, str]:
        project = self.get(db, project_id)
        requirements, architecture, database, tasks, roles, documents = self.requirements(db, project_id), self.architecture(db, project_id), self.database(db, project_id), self.tasks(db, project_id), self.roles(db, project_id), self.documents(db, project_id)
        data = {"project": ProjectDetail.model_validate(self.detail(db, project_id)).model_dump(mode="json"), "requirements": [item.model_dump(mode="json") for item in requirements], "architecture": architecture.model_dump(mode="json") if architecture else None, "database": [item.model_dump(mode="json") for item in database], "tasks": [item.model_dump(mode="json") for item in tasks], "roles": [item.model_dump(mode="json") for item in roles], "documents": [item.model_dump(mode="json") for item in documents]}
        safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "-", project.name).strip("-")[:60] or "project"
        if format_name == "json":
            return json.dumps(data, indent=2), "application/json", safe_name + ".json"
        if format_name == "markdown":
            return (documents[0].content if documents else f"# {project.name}\n\n{project.description}\n"), "text/markdown; charset=utf-8", safe_name + ".md"
        raise HTTPException(status_code=400, detail={"code": "invalid_export_format", "message": "format must be markdown or json"})

    @staticmethod
    def _slug(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", ".", name.lower()).strip(".") or "person"

    @staticmethod
    def _get_or_create_person(db: Session, name: str, email: str, title: str) -> Person:
        person = db.scalar(select(Person).where(Person.email == email))
        if person:
            return person
        person = Person(name=name, email=email, title=title)
        db.add(person)
        db.flush()
        return person

    @staticmethod
    def _progress(project: Project) -> int:
        tasks = project.tasks
        return round(sum(1 for item in tasks if item.status == "done") / len(tasks) * 100) if tasks else 0

    @staticmethod
    def _health(project: Project) -> int:
        requirements = len(project.requirements)
        tasks = len(project.tasks)
        return min(96, 58 + min(requirements, 10) * 2 + min(tasks, 10))

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import Response as RawResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import AnalyzeOut, ArchitectureOut, DatabaseEntityOut, DocumentOut, GenerationRunOut, ProjectCreate, ProjectDetail, ProjectSummary, RequirementOut, TaskOut, TeamRoleOut
from app.services.planning_service import PlanningService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])
service = ProjectService()


@router.post("", response_model=ProjectSummary, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    return service.create(db, data)


@router.get("", response_model=list[ProjectSummary])
def list_projects(db: Session = Depends(get_db)):
    return service.list(db)


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    return service.detail(db, project_id)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    service.delete(db, project_id)
    return Response(status_code=204)


@router.post("/{project_id}/analyze", response_model=AnalyzeOut)
def analyze_project(project_id: UUID, db: Session = Depends(get_db)):
    run = PlanningService().analyze(db, project_id)
    return AnalyzeOut(run_id=run.id, status=run.status, message="Project blueprint generated successfully")


@router.get("/{project_id}/requirements", response_model=list[RequirementOut])
def get_requirements(project_id: UUID, db: Session = Depends(get_db)):
    return service.requirements(db, project_id)


@router.get("/{project_id}/architecture", response_model=ArchitectureOut | None)
def get_architecture(project_id: UUID, db: Session = Depends(get_db)):
    return service.architecture(db, project_id)


@router.get("/{project_id}/database", response_model=list[DatabaseEntityOut])
def get_database(project_id: UUID, db: Session = Depends(get_db)):
    return service.database(db, project_id)


@router.get("/{project_id}/tasks", response_model=list[TaskOut])
def get_tasks(project_id: UUID, db: Session = Depends(get_db)):
    return service.tasks(db, project_id)


@router.post("/{project_id}/tasks/regenerate", response_model=AnalyzeOut)
def regenerate_tasks(project_id: UUID, db: Session = Depends(get_db)):
    run = PlanningService().analyze(db, project_id)
    return AnalyzeOut(run_id=run.id, status=run.status, message="Tasks regenerated with the validated blueprint")


@router.get("/{project_id}/team", response_model=list[TeamRoleOut])
def get_team(project_id: UUID, db: Session = Depends(get_db)):
    return service.roles(db, project_id)


@router.get("/{project_id}/documentation", response_model=list[DocumentOut])
def get_documentation(project_id: UUID, db: Session = Depends(get_db)):
    return service.documents(db, project_id)


@router.get("/{project_id}/generation-runs", response_model=list[GenerationRunOut])
def get_generation_runs(project_id: UUID, db: Session = Depends(get_db)):
    return service.runs(db, project_id)


@router.get("/{project_id}/export")
def export_project(project_id: UUID, format: str = Query(default="markdown"), db: Session = Depends(get_db)):
    content, media_type, filename = service.export(db, project_id, format)
    return RawResponse(content=content, media_type=media_type, headers={"Content-Disposition": f'attachment; filename="{filename}"'})

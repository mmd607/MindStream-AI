from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import Response as RawResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import APIOut, ActivityOut, AnalyzeOut, ArchitectureOut, DatabaseEntityOut, DocumentOut, FeatureOut, GenerationRunOut, InsightOut, MilestoneOut, PersonOut, ProjectComparison, ProjectCreate, ProjectDetail, ProjectMemberOut, ProjectStatusUpdate, ProjectSummary, ReportOut, ReportUpdate, RequirementOut, RiskOut, SearchOut, TaskOut, TeamRoleOut, TraceabilityLink, WorkspaceOut
from app.services.planning_service import PlanningService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])
service = ProjectService()


@router.post("", response_model=ProjectSummary, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    return service.create(db, data)


@router.get("/workspace", response_model=WorkspaceOut)
def workspace(db: Session = Depends(get_db)):
    return service.workspace(db)


@router.get("/people", response_model=list[PersonOut])
def list_people(search: str = Query(default="", max_length=120), db: Session = Depends(get_db)):
    return service.people(db, search)


@router.get("/people/{person_id}", response_model=PersonOut)
def get_person(person_id: UUID, db: Session = Depends(get_db)):
    return service.person(db, person_id)


@router.get("/reports/{report_id}", response_model=ReportOut)
def get_report(report_id: UUID, db: Session = Depends(get_db)):
    return service.report(db, report_id)


@router.patch("/reports/{report_id}", response_model=ReportOut)
def update_report(report_id: UUID, data: ReportUpdate, db: Session = Depends(get_db)):
    return service.update_report(db, report_id, data.status)


@router.get("/compare", response_model=list[ProjectComparison])
def compare_projects(ids: list[UUID] | None = Query(default=None), db: Session = Depends(get_db)):
    return service.compare(db, ids or [])


@router.get("/search", response_model=SearchOut)
def search_workspace(q: str = Query(min_length=2, max_length=120), db: Session = Depends(get_db)):
    return service.search(db, q)


@router.get("", response_model=list[ProjectSummary])
def list_projects(search: str = Query(default="", max_length=120), status: str = Query(default="", max_length=30), domain: str = Query(default="", max_length=80), db: Session = Depends(get_db)):
    return service.list(db, search, status, domain)


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    return service.detail(db, project_id)


@router.patch("/{project_id}", response_model=ProjectSummary)
def update_project_status(project_id: UUID, data: ProjectStatusUpdate, db: Session = Depends(get_db)):
    return service.update_status(db, project_id, data.status, data.reason)


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


@router.get("/{project_id}/features", response_model=list[FeatureOut])
def get_features(project_id: UUID, db: Session = Depends(get_db)):
    return service.features(db, project_id)


@router.get("/{project_id}/traceability", response_model=list[TraceabilityLink])
def get_traceability(project_id: UUID, db: Session = Depends(get_db)):
    return service.traceability(db, project_id)


@router.get("/{project_id}/insights", response_model=list[InsightOut])
def get_insights(project_id: UUID, db: Session = Depends(get_db)):
    return service.insights(db, project_id)


@router.get("/{project_id}/apis", response_model=list[APIOut])
def get_apis(project_id: UUID, search: str = Query(default="", max_length=120), method: str = Query(default="", max_length=10), module: str = Query(default="", max_length=120), db: Session = Depends(get_db)):
    return service.apis(db, project_id, search, method, module)


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


@router.get("/{project_id}/people", response_model=list[ProjectMemberOut])
def get_people(project_id: UUID, db: Session = Depends(get_db)):
    return service.members(db, project_id)


@router.get("/{project_id}/reports", response_model=list[ReportOut])
def get_reports(project_id: UUID, db: Session = Depends(get_db), report_type: str = Query(default="", max_length=50), status: str = Query(default="", max_length=30)):
    reports = service.reports(db, project_id)
    return [item for item in reports if (not report_type or item.report_type == report_type) and (not status or item.status == status)]


@router.post("/{project_id}/reports", response_model=ReportOut, status_code=201)
def generate_report(project_id: UUID, report_type: str = Query(default="health", max_length=50), db: Session = Depends(get_db)):
    return service.generate_report(db, project_id, report_type)


@router.get("/{project_id}/activities", response_model=list[ActivityOut])
def get_activities(project_id: UUID, db: Session = Depends(get_db)):
    return service.activities(db, project_id)


@router.get("/{project_id}/milestones", response_model=list[MilestoneOut])
def get_milestones(project_id: UUID, db: Session = Depends(get_db)):
    return service.milestones(db, project_id)


@router.get("/{project_id}/risks", response_model=list[RiskOut])
def get_risks(project_id: UUID, db: Session = Depends(get_db)):
    return service.risks(db, project_id)


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

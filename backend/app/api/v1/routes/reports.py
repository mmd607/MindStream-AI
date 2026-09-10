from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import ReportOut
from app.services.project_service import ProjectService

router = APIRouter(prefix="/reports", tags=["reports"])
service = ProjectService()


@router.get("", response_model=list[ReportOut])
def list_reports(report_type: str = Query(default="", max_length=50), status: str = Query(default="", max_length=30), db: Session = Depends(get_db)):
    return service.reports_all(db, report_type, status)

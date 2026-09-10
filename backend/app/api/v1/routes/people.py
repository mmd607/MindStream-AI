from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import PersonOut, ProjectSummary
from app.services.project_service import ProjectService

router = APIRouter(prefix="/people", tags=["people"])
service = ProjectService()


@router.get("", response_model=list[PersonOut])
def list_people(search: str = Query(default="", max_length=120), db: Session = Depends(get_db)):
    return service.people(db, search)


@router.get("/{person_id}", response_model=PersonOut)
def get_person(person_id: UUID, db: Session = Depends(get_db)):
    return service.person(db, person_id)


@router.get("/{person_id}/projects", response_model=list[ProjectSummary])
def get_person_projects(person_id: UUID, db: Session = Depends(get_db)):
    return service.person_projects(db, person_id)

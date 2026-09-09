import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import GenerationRun
from app.planners.orchestrator import PlanningOrchestrator
from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class PlanningService:
    def analyze(self, db: Session, project_id: UUID) -> GenerationRun:
        project = ProjectService().get(db, project_id)
        active = db.scalar(select(GenerationRun).where(GenerationRun.project_id == project_id, GenerationRun.status.in_(["queued", "running"])))
        if active:
            raise HTTPException(status_code=409, detail={"code": "generation_in_progress", "message": "A generation run is already in progress"})
        run = GenerationRun(project_id=project_id, run_type="full", status="queued")
        db.add(run)
        db.commit()
        try:
            PlanningOrchestrator().run(db, project, run)
            db.commit()
        except Exception as exc:
            db.rollback()
            run = db.get(GenerationRun, run.id)
            if run:
                run.status = "failed"
                run.error_message = f"{exc.__class__.__name__}: generation stage failed"
                run.completed_at = datetime.now(timezone.utc)
                db.commit()
            logger.exception("generation_failed project_id=%s", project_id)
            raise HTTPException(status_code=422, detail={"code": "generation_failed", "message": "The project plan could not be generated. Review the generation run for details."}) from exc
        return run

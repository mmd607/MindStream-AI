from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.projects import router as project_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import Base, SessionLocal, engine
from app import models  # noqa: F401 - registers all ORM models
from app.services.demo_seed import seed_demo_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    # This keeps the zero-setup SQLite demo runnable. Production deployments should apply Alembic migrations.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    yield


configure_logging(settings.log_level)
app = FastAPI(title="AI Project Architect API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=False, allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Content-Type"])
app.include_router(health_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def safe_exception_handler(_: Request, __: Exception):
    return JSONResponse(status_code=500, content={"code": "internal_error", "message": "An unexpected error occurred"})


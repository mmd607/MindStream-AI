# Backend Specification

## Stack
Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL, pytest.

## Structure

```text
backend/app/
├── api/v1/routes/
├── ai/
├── core/
├── db/
├── models/
├── schemas/
├── services/
├── planners/
└── main.py
```

## Services
Implement clear services such as:
- ProjectService
- PlanningService
- ArchitectureService
- TaskService
- DocumentationService

## AI Provider
Define a provider interface such as:
`generate_structured(prompt, schema) -> validated result`

Implement mock and real providers against the same contract.

## Mock Mode
Mock mode must be deterministic and runnable without credentials.

## Database
Use Alembic migrations. Do not rely on arbitrary SQL executed at startup.

## Testing
Cover project CRUD, validation, mock generation, dependency cycle detection, orchestration, and major API endpoints.

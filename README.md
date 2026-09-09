# AI Project Architect

AI Project Architect turns a natural-language software idea into a coherent project blueprint: requirements, architecture, database design, API/module boundaries, implementation tasks, team assignments, dependencies, documentation, and Markdown/JSON exports.

## MVP status

This is a portfolio-ready modular monolith. The default mock AI provider is deterministic and works without an API key. The real provider adapter is intentionally isolated and requires an OpenAI-compatible endpoint configuration before use.

## Stack

- Backend: Python 3.11+, FastAPI, SQLAlchemy 2, Pydantic, Alembic, pytest
- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Intended local deployment: Docker Compose + PostgreSQL
- Test fallback: SQLite

## Run locally without Docker

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload
```

In a second terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open http://localhost:3000. The API is at http://localhost:8000 and its OpenAPI docs are at http://localhost:8000/docs.

To apply the database migration explicitly before starting the backend:

```powershell
alembic -c backend\alembic.ini upgrade head
```

## Docker Compose

Docker is not installed in the current development environment, but the repository includes a complete Compose setup:

```bash
docker compose up --build
```

Compose uses PostgreSQL. The manual default uses SQLite for a zero-dependency demo; set `DATABASE_URL` to a PostgreSQL URL when PostgreSQL is available.

## Tests

```powershell
pip install -r backend\requirements.txt
pytest backend\tests -q
```

Frontend verification commands:

```powershell
cd frontend
npm.cmd ci
npm.cmd run lint
npm.cmd exec tsc -- --noEmit
npm.cmd run build
```

## AI provider configuration

`AI_PROVIDER=mock` is the safe default. It produces realistic deterministic plans based on the project description and is used by the test suite. `AI_PROVIDER=real` selects the provider abstraction, which expects `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL`; generated text is still validated before it can become application state. User input and generated content are treated as untrusted data, and the app never executes generated code or commands.

## Project structure

```text
backend/app/{api,ai,core,db,models,planners,schemas,services}
frontend/{app,components,lib,types}
docs/
specification/
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/API.md](docs/API.md), [docs/SECURITY.md](docs/SECURITY.md), and [docs/ROADMAP.md](docs/ROADMAP.md).

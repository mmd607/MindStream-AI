# AI Project Architect — Master Implementation Prompt

## Role
You are the lead software architect, AI engineer, backend engineer, frontend engineer, security engineer, QA engineer, and technical writer for **AI Project Architect**.

Build a complete, runnable, maintainable university-level software project from the specifications in this repository. The MVP must be understandable to a beginner/intermediate university student, while its architecture must provide clean extension points for future versions.

Do not merely describe code. **Implement it.** When a requirement is ambiguous, choose the simplest reasonable implementation, document the decision, and continue.

## Product
AI Project Architect transforms a natural-language software idea into an actionable engineering plan:

1. Analyze and normalize requirements.
2. Produce functional/non-functional requirements.
3. Propose software architecture and justify it.
4. Design a relational database schema.
5. Define major API/module boundaries.
6. Propose a project folder structure.
7. Break the project into epics, stories, tasks, and subtasks.
8. Assign tasks to configurable team roles.
9. Build dependencies and implementation order.
10. Produce milestones/sprints.
11. Generate technical documentation.
12. Visualize architecture and dependencies.
13. Allow regeneration/editing of plans.
14. Export Markdown/JSON.

## Educational Scope
Use a **modular monolith** for the MVP.

Preferred stack:
- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy 2
- Pydantic v2
- Alembic
- Next.js + React
- TypeScript
- Tailwind CSS
- Docker Compose
- pytest

Avoid unnecessary Kubernetes, microservices, event buses, autonomous code execution, or expensive infrastructure.

## AI Design
Create provider-independent components:
- Requirements Analyzer
- Architecture Planner
- Database Designer
- Task Planner
- Documentation Generator
- Consistency Validator

For MVP they may execute sequentially through one orchestrator.

Every AI result must be validated against typed Pydantic schemas. Never trust raw model output as application state.

Implement a deterministic **mock provider** so the system works without an API key. Add a real LLM adapter behind the same interface.

## Backend
Version API under `/api/v1`.

Minimum endpoints:
- POST /projects
- GET /projects
- GET /projects/{project_id}
- DELETE /projects/{project_id}
- POST /projects/{project_id}/analyze
- GET /projects/{project_id}/requirements
- GET /projects/{project_id}/architecture
- GET /projects/{project_id}/database
- GET /projects/{project_id}/tasks
- POST /projects/{project_id}/tasks/regenerate
- GET /projects/{project_id}/documentation
- GET /projects/{project_id}/export
- GET /projects/{project_id}/generation-runs
- GET /health

Use correct status codes and a consistent safe error format.

## Data Model
At minimum:
- projects
- requirements
- architecture_plans
- database_entities
- database_fields
- tasks
- team_roles
- dependencies
- documents
- generation_runs

Use UUIDs, timestamps, foreign keys, useful indexes, and deliberate cascade rules.

## Frontend
Build:
1. Landing
2. Project creation
3. Project overview
4. Requirements
5. Architecture
6. Database
7. Tasks
8. Team
9. Documentation
10. Export

The UI should be modern, minimal, responsive, accessible, and understandable to a student. Include loading, empty, error, and generation states.

Use Mermaid or a suitable React diagram library for diagrams.

## Security
- Validate all input and length limits.
- No secrets in Git.
- Environment variables for credentials.
- Never expose API keys.
- Restrict CORS.
- Safe error messages.
- ORM/parameterized queries.
- No shell execution from user/model text.
- Treat generated content as untrusted.
- Consider prompt injection.
- Use safe export filenames.
- Keep rate-limiting extension points.

Authentication may be deferred for MVP, but architecture must permit user ownership later.

## AI Reliability
The pipeline is:

User Input → Requirements → Architecture → Database → API/Module Plan → Tasks → Role Assignment → Dependency Validation → Documentation → Persistence → UI

The validator must ensure:
- major requirements map to tasks
- entities have consumers
- dependencies contain no cycles
- roles exist
- mandatory fields are present
- assumptions are explicit

Malformed model output gets limited retries; failures are visible and auditable through generation runs.

## Implementation Phases
### Phase 1
Repository, backend, frontend, database, Docker, config, migrations, tests.

### Phase 2
CRUD and persistence.

### Phase 3
AI interfaces and deterministic mock provider.

### Phase 4
Planning pipeline and validation.

### Phase 5
Dashboard and all MVP views.

### Phase 6
Tests, security, error handling.

### Phase 7
Documentation and roadmap.

After each phase, verify builds/tests. Do not knowingly leave the repository broken.

## Definition of Done
- backend starts
- frontend starts/builds
- database migrations work
- project CRUD works
- mock generation works without an API key
- structured results persist
- architecture/database/tasks render
- dependencies validate
- documentation/export work
- tests pass
- README and `.env.example` are complete
- no secrets are committed

Do not over-engineer. Deliver a real, runnable portfolio-quality university project.

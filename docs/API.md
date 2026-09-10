# API

Base URL: `/api/v1`

The API provides project CRUD, synchronous deterministic mock generation, blueprint retrieval, workspace intelligence, multi-project people, reports, activity, milestones, risks, traceability, API exploration, comparison, and safe Markdown/JSON export. FastAPI also publishes interactive OpenAPI documentation at `/docs`.

Main endpoints: `GET /projects/workspace`, `GET /projects/search?q=...`, `POST /projects`, `GET /projects`, `PATCH /projects/{id}`, `DELETE /projects/{id}`, `POST /projects/{id}/analyze`, and `POST /projects/{id}/seed-demo`. Blueprint endpoints include `GET /projects/{id}/requirements`, `/features`, `/traceability`, `/insights`, `/architecture`, `/database`, `/apis`, `/tasks`, `/team`, `/documentation`, `/generation-runs`, and `/export?format=markdown|json`; task regeneration is available at `POST /projects/{id}/tasks/regenerate`.

Workspace relationship endpoints include `GET /people`, `GET /people/{id}`, `GET /people/{id}/projects`, plus the backward-compatible `/projects/people` aliases. Reports are available through `GET /reports`, `GET/POST /projects/{id}/reports`, `POST /projects/{id}/reports/{report_id}/regenerate`, and `GET/PATCH /projects/reports/{id}`. Project intelligence also exposes `GET /projects/{id}/people`, `/milestones`, `/risks`, and `/activities`.


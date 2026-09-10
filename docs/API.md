# API

Base URL: `/api/v1`

The API provides project CRUD, synchronous deterministic mock generation, blueprint retrieval, workspace intelligence, multi-project people, reports, activity, milestones, risks, traceability, API exploration, comparison, and safe Markdown/JSON export. FastAPI also publishes interactive OpenAPI documentation at `/docs`.

Main endpoints: `GET /projects/workspace`, `GET /projects/search?q=...`, `POST /projects`, `GET /projects`, `PATCH /projects/{id}`, `GET /projects/people`, `GET /projects/people/{id}`, `GET /projects/compare?ids=...`, `GET /projects/{id}`, `DELETE /projects/{id}`, `POST /projects/{id}/analyze`, `GET /projects/{id}/requirements`, `GET /projects/{id}/features`, `GET /projects/{id}/traceability`, `GET /projects/{id}/insights`, `GET /projects/{id}/architecture`, `GET /projects/{id}/database`, `GET /projects/{id}/apis`, `GET /projects/{id}/tasks`, `POST /projects/{id}/tasks/regenerate`, `GET /projects/{id}/team`, `GET /projects/{id}/people`, `GET /projects/{id}/reports`, `POST /projects/{id}/reports`, `GET/PATCH /projects/reports/{id}`, `GET /projects/{id}/milestones`, `GET /projects/{id}/risks`, `GET /projects/{id}/activities`, `GET /projects/{id}/documentation`, `GET /projects/{id}/generation-runs`, and `GET /projects/{id}/export?format=markdown|json`.


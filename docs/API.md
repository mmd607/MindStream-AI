# API

Base URL: `/api/v1`

The API provides project CRUD, synchronous mock generation, blueprint retrieval, team roles, generation runs, and safe Markdown/JSON export. FastAPI also publishes interactive OpenAPI documentation at `/docs`.

Main endpoints: `POST /projects`, `GET /projects`, `GET /projects/{id}`, `DELETE /projects/{id}`, `POST /projects/{id}/analyze`, `GET /projects/{id}/requirements`, `GET /projects/{id}/architecture`, `GET /projects/{id}/database`, `GET /projects/{id}/tasks`, `POST /projects/{id}/tasks/regenerate`, `GET /projects/{id}/team`, `GET /projects/{id}/documentation`, `GET /projects/{id}/generation-runs`, and `GET /projects/{id}/export?format=markdown|json`.


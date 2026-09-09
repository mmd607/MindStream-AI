# API Contract

Base path: `/api/v1`

## Projects
- POST `/projects`
- GET `/projects`
- GET `/projects/{id}`
- DELETE `/projects/{id}`

## Planning
- POST `/projects/{id}/analyze`
- GET `/projects/{id}/generation-runs`

## Results
- GET `/projects/{id}/requirements`
- GET `/projects/{id}/architecture`
- GET `/projects/{id}/database`
- GET `/projects/{id}/tasks`
- POST `/projects/{id}/tasks/regenerate`
- GET `/projects/{id}/documentation`
- GET `/projects/{id}/export`

## Health
GET `/health`

Every endpoint validates input, uses predictable JSON, correct status codes, and safe error messages.

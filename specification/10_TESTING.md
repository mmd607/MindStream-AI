# Testing Strategy

## Backend
Use pytest.

### Unit
- schema validation
- planner outputs
- dependency cycle detection
- role validation
- mock provider
- orchestration

### API
- project CRUD
- analyze
- requirements
- architecture
- database
- tasks
- export

### Negative
- missing name
- oversized description
- invalid UUID
- missing project
- malformed planner output
- cyclic dependency
- invalid task status

## Frontend
Test form validation, loading/error states, task filtering, and core rendering.

## End-to-End
Create project → run mock analysis → retrieve results → display tasks → export.

# Database Design

## Main Tables

### projects
id UUID PK, name, description, target_users, preferred_stack, team_size, status, created_at, updated_at.

### requirements
id UUID PK, project_id FK, category, title, description, priority, source, created_at.

### architecture_plans
id UUID PK, project_id FK, style, rationale, components_json, technologies_json, created_at, updated_at.

### database_entities
id UUID PK, project_id FK, name, description.

### database_fields
id UUID PK, entity_id FK, name, data_type, nullable, primary_key, unique, default_value.

### team_roles
id UUID PK, project_id FK, name, description.

### tasks
id UUID PK, project_id FK, parent_id nullable FK, title, description, task_type, priority, status, effort, acceptance_criteria, role_id nullable FK.

### dependencies
id UUID PK, task_id FK, depends_on_task_id FK.

### documents
id UUID PK, project_id FK, document_type, content, version, created_at.

### generation_runs
id UUID PK, project_id FK, run_type, status, started_at, completed_at, error_message.

Use foreign keys, indexes on project_id, and deliberate cascade rules. Validate dependency cycles at application level.

# Database

The SQLAlchemy models cover `projects`, `project_workspace_metadata`, `requirements`, `project_features`, `architecture_plans`, `project_apis`, `database_entities`, `database_fields`, `team_roles`, `tasks`, `task_assignments`, `dependencies`, `documents`, `generation_runs`, `people`, `project_memberships`, `reports`, `activities`, `milestones`, and `project_risks`. UUID primary keys, foreign keys, indexes, uniqueness constraints, timestamps, and cascade behavior are defined in `backend/app/models/entities.py`.

`project_memberships` enables one person to participate in multiple projects, while `task_assignments` provides the concrete Task → Person relationship used by task, team, API, and traceability views. Feature and API records are generated from the validated blueprint and retain links back to requirements and delivery tasks. The `c3f1_workspace_intelligence` and `d7a2_task_assignments` migrations add workspace data without removing existing records; the latter safely upgrades databases where the earlier workspace migration has already been applied.

Apply the initial Alembic migration from the repository root with `alembic -c backend/alembic.ini upgrade head`. PostgreSQL is the intended deployment database; SQLite is the local zero-setup fallback.


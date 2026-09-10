# Database

The SQLAlchemy models cover `projects`, `project_workspace_metadata`, `requirements`, `project_features`, `architecture_plans`, `project_apis`, `database_entities`, `database_fields`, `team_roles`, `tasks`, `dependencies`, `documents`, `generation_runs`, `people`, `project_memberships`, `reports`, `activities`, `milestones`, and `project_risks`. UUID primary keys, foreign keys, indexes, uniqueness constraints, timestamps, and cascade behavior are defined in `backend/app/models/entities.py`.

`project_memberships` enables one person to participate in multiple projects. Feature and API records are generated from the validated blueprint and retain links back to requirements and delivery tasks. The `c3f1_workspace_intelligence` migration adds the workspace tables without removing existing records.

Apply the initial Alembic migration from the repository root with `alembic -c backend/alembic.ini upgrade head`. PostgreSQL is the intended deployment database; SQLite is the local zero-setup fallback.


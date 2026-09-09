# Database

The SQLAlchemy models cover `projects`, `requirements`, `architecture_plans`, `database_entities`, `database_fields`, `team_roles`, `tasks`, `dependencies`, `documents`, and `generation_runs`. UUID primary keys, foreign keys, indexes, uniqueness constraints, timestamps, and cascade behavior are defined in `backend/app/models/entities.py`.

Apply the initial Alembic migration from the repository root with `alembic -c backend/alembic.ini upgrade head`. PostgreSQL is the intended deployment database; SQLite is the local zero-setup fallback.


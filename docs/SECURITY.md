# Security

- Project input is bounded with Pydantic length and collection limits.
- SQLAlchemy handles database operations; user text is never interpolated into SQL.
- Provider keys remain server-side environment variables.
- CORS is restricted to `FRONTEND_ORIGIN`.
- Errors returned to clients use safe messages without stack traces or paths.
- Project descriptions and generated plans are untrusted data. No generated code, shell command, SQL, or filesystem operation is executed.
- Export filenames are derived from the project name with a strict safe-character allowlist.
- Authentication, rate limiting, and project ownership are deliberate future extension points.


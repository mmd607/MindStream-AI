# DevOps and Local Deployment

## Docker Compose
Provide:
- backend
- frontend
- postgres

## Environment
Provide `.env.example` with placeholders for database URL, LLM provider, API key, and frontend origin. Never commit real secrets.

## Health
Backend exposes `/health`.

## Local Setup
Document both:
1. Docker Compose workflow.
2. Manual backend/frontend workflow.

## CI
Future CI should install dependencies, lint, test, build frontend, and build backend image.

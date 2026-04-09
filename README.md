# TaskFlow (Backend-only Submission)

## 1. Overview
TaskFlow is a backend-only task management API built with FastAPI, SQLAlchemy, Alembic, and PostgreSQL.

Implemented backend scope for this assignment:
- JWT auth foundation with bcrypt password utilities and token helpers.
- Core data model (`users`, `projects`, `tasks`) via Alembic migration.
- Centralized JSON error handling with required 400/401/403/404 contracts.
- Dockerized API + PostgreSQL setup with migration-on-start behavior.
- Seed SQL and basic API test scaffold.

Tech stack:
- Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16, Docker Compose.

## 2. Architecture Decisions
- Layered backend structure (`api`, `core`, `db`, `models`, `utils`, `exceptions`) to keep concerns separated.
- Strongly validated env config in one place (`app/core/config.py`) using `pydantic-settings`.
- Centralized exception mapping to enforce consistent API contracts.
- UUID primary keys and explicit foreign keys/indexes for data integrity and query performance.
- Docker uses a multi-stage API image build for a smaller runtime image.

Tradeoffs and current limitations:
- Auth dependencies, JWT utilities, and exception contracts are implemented, but full CRUD business flows are still scaffold-level for some endpoints.
- Seed file is SQL-first for reviewer setup speed instead of app-level seed orchestration.

## 3. Running Locally
```bash
git clone https://github.com/nutan1202/taskflow-Nutan
cd taskflow-Nutan
cp .env.example .env
docker compose up --build
```

API base URL:
- `http://localhost:8000`

Notes:
- This backend-only submission does not include a React frontend.
- API and DB are started by `docker compose up`.

## 4. Running Migrations
Migrations run automatically on API container startup via `backend/docker-entrypoint.sh`.

Manual migration commands:
```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic downgrade -1
```

## 5. Test Credentials
Seed credentials (from `backend/scripts/seed.sql`):

```
Email:    test@example.com
Password: password123
```

## 6. API Reference
Authentication:
- `POST /auth/register`
- `POST /auth/login`

Projects:
- `GET /projects`
- `POST /projects`
- `GET /projects/:id`
- `PATCH /projects/:id`
- `DELETE /projects/:id`

Tasks:
- `GET /projects/:id/tasks?status=&assignee=`
- `POST /projects/:id/tasks`
- `PATCH /tasks/:id`
- `DELETE /tasks/:id`

Health:
- `GET /health`

Error response contracts:
- `400` validation:
  - `{ "error": "validation failed", "fields": { "email": "is required" } }`
- `401` unauthenticated:
  - `{ "error": "unauthorized" }`
- `403` forbidden:
  - `{ "error": "forbidden" }`
- `404` not found:
  - `{ "error": "not found" }`

Backend-only evidence requirement:
- Test suite exists in `backend/tests/` as required alternative to frontend.

## 7. What You'd Do With More Time
- Complete and harden all auth/project/task endpoint business logic end-to-end.
- Add integration tests for auth and task lifecycle flows (minimum 3, including failure paths).
- Add pagination and project stats endpoint (`GET /projects/:id/stats`).
- Add request/response schemas for stricter API contracts and OpenAPI examples.
- Add CI pipeline for lint/test/build gates on pull requests.

## Environment Files
- `.env.example` (root): canonical Docker Compose + API runtime variables.
- `backend/.env.backend.example`: backend-only local run without Docker Compose.

Both files are template-only; do not commit `.env` files or real secrets.

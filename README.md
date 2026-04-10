# TaskFlow (Backend-Only Submission)

## 1. Overview
This submission is **backend-only** and implements the TaskFlow API using FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic, and Docker Compose.

Scope included in this submission:
- JWT-based authentication (`register`, `login`, bearer-protected business routes)
- Project APIs (list, create, detail, update, delete)
- Task APIs (list/create under project, update/delete by task id)
- Project stats API (`GET /projects/{project_id}/stats`)
- Standardized JSON error contracts (`400`, `401`, `403`, `404`)
- Containerized startup with automatic migration + seed flow
- Structured JSON logging and graceful shutdown behavior for container runtime

## 2. Architecture Decisions
- **FastAPI over Go for this submission:** I chose FastAPI for faster delivery in the assignment timebox, strong request/response validation with Pydantic, and built-in OpenAPI docs. Go remains a strong production option, but FastAPI gave a faster path to a complete and reviewable API here.
- **SQLAlchemy 2.0 + Alembic:** SQLAlchemy 2.0 gives explicit ORM patterns; Alembic provides reproducible, versioned schema changes.
- **PostgreSQL:** The `users/projects/tasks` relational model benefits from PostgreSQL constraints, enum support, and query behavior.
- **Layered structure:** Routes -> Services -> Repositories separates HTTP, business logic, and data access.
- **Docker Compose first:** Reviewer can run the backend with Docker only.

## 3. Running Locally
Assumption: reviewer has **Docker + Docker Compose** installed.

```bash
git clone https://github.com/nutan1202/taskflow-Nutan
cd taskflow-Nutan
docker compose up --build
```

What `docker compose up --build` does:
- Starts `db` (PostgreSQL 16)
- Builds and starts `api` (FastAPI)
- `api` entrypoint waits for DB, runs migrations, optionally seeds, then starts Uvicorn

Optional overrides:
- You can create a root `.env` file from `.env.example` only if you want to override defaults (ports, DB creds, JWT secret, seed behavior).
- No `.env` file is required for first run.

Useful follow-up commands:
```bash
# stop services
docker compose down

# stop and remove DB volume (fresh DB next run)
docker compose down -v
```

Base URL after startup:
- `http://localhost:8000`

Interactive API docs after startup:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Auth model:
- `POST /auth/register` and `POST /auth/login` are public
- `GET /health` is public
- All project/task/stats business endpoints require `Authorization: Bearer <token>`

## 4. Running Migrations
Automatic behavior on container start:
- `alembic upgrade head` runs from `backend/docker-entrypoint.sh`

Manual migration commands (inside running API container):
```bash
# apply latest migrations
docker compose exec api alembic upgrade head

# rollback one migration
docker compose exec api alembic downgrade -1
```

Seed behavior:
- Controlled by `RUN_DB_SEED` in `.env` (default `true`)
- When enabled, `python scripts/seed.py` runs on startup
- Seed script is idempotent (safe across restarts; inserts only when missing)

## 5. Test Credentials
Use these seeded credentials for reviewer login:

- Email: `test@example.com`
- Password: `password123`

## 6. API Reference
All responses are JSON.

### Authorization Rules
- All project/task/stats business endpoints require bearer authentication.
- Project update/delete is owner-only.
- Project detail, task listing, and project stats are accessible to users who own the project or have task membership in it.
- Task delete is allowed only for project owner or task creator.

### Authentication
1. `POST /auth/register`
- Request:
```json
{
  "name": "Reviewer User",
  "email": "reviewer@example.com",
  "password": "password123"
}
```
- Response `201`:
```json
{
  "token": "<jwt>",
  "user": {
    "id": "uuid",
    "name": "Reviewer User",
    "email": "reviewer@example.com",
    "created_at": "2026-04-10T00:00:00Z"
  }
}
```

2. `POST /auth/login`
- Request:
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```
- Response `200`: same shape as register

### Health
1. `GET /health` (public)
- Response `200`:
```json
{ "status": "ok" }
```

### Projects
1. `GET /projects`
- Query params:
  - `page` (default `1`, min `1`)
  - `limit` (default `20`, min `1`, max `100`)
- Response `200`:
```json
{
  "projects": [
    {
      "id": "uuid",
      "name": "TaskFlow Demo Project",
      "description": "Seeded project for reviewer testing",
      "owner_id": "uuid",
      "created_at": "2026-04-10T00:00:00Z"
    }
  ],
  "page": 1,
  "limit": 20,
  "total": 1
}
```

2. `POST /projects`
- Request:
```json
{
  "name": "Sprint Alpha",
  "description": "Execution board"
}
```
- Response `201`:
```json
{
  "id": "uuid",
  "name": "Sprint Alpha",
  "description": "Execution board",
  "owner_id": "uuid",
  "created_at": "2026-04-10T00:00:00Z"
}
```

3. `GET /projects/{project_id}`
- Response `200`:
```json
{
  "id": "uuid",
  "name": "Sprint Alpha",
  "description": "Execution board",
  "owner_id": "uuid",
  "created_at": "2026-04-10T00:00:00Z",
  "tasks": [
    {
      "id": "uuid",
      "title": "Task A",
      "description": null,
      "status": "todo",
      "priority": "medium",
      "project_id": "uuid",
      "assignee_id": "uuid",
      "due_date": null,
      "created_at": "2026-04-10T00:00:00Z",
      "updated_at": "2026-04-10T00:00:00Z"
    }
  ]
}
```

4. `PATCH /projects/{project_id}`
- Request (partial update allowed):
```json
{
  "name": "Sprint Alpha (Updated)",
  "description": "Updated description"
}
```
- Response `200`: updated project object

5. `DELETE /projects/{project_id}`
- Response `204` (no body)

6. `GET /projects/{project_id}/stats`
- Response `200`:
```json
{
  "project_id": "uuid",
  "counts_by_status": {
    "todo": 1,
    "in_progress": 1,
    "done": 1
  },
  "counts_by_assignee": [
    {
      "assignee_id": "uuid",
      "assignee_name": "Test User",
      "count": 3
    }
  ]
}
```

### Tasks
1. `GET /projects/{project_id}/tasks`
- Query params:
  - `status` (optional: `todo` | `in_progress` | `done`)
  - `assignee` (optional UUID)
  - `page` (default `1`, min `1`)
  - `limit` (default `20`, min `1`, max `100`)
- Example:
  - `GET /projects/{project_id}/tasks?status=todo&assignee=<user_uuid>&page=1&limit=20`
- Response `200`:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Seed task: todo",
      "description": "Initial task in todo state",
      "status": "todo",
      "priority": "medium",
      "project_id": "uuid",
      "assignee_id": "uuid",
      "creator_id": "uuid",
      "due_date": "2026-04-13",
      "created_at": "2026-04-10T00:00:00Z",
      "updated_at": "2026-04-10T00:00:00Z"
    }
  ],
  "page": 1,
  "limit": 20,
  "total": 1
}
```

2. `POST /projects/{project_id}/tasks`
- Request:
```json
{
  "title": "Prepare API review notes",
  "description": "Summarize endpoints and constraints",
  "priority": "high",
  "assignee_id": "<user_uuid>",
  "due_date": "2026-04-20"
}
```
- Response `201`: task object

3. `PATCH /tasks/{task_id}`
- Request (any subset):
```json
{
  "status": "in_progress",
  "priority": "medium",
  "title": "Prepare API review notes v2"
}
```
- Response `200`:
```json
{
  "id": "uuid",
  "title": "Prepare API review notes v2",
  "description": "Summarize endpoints and constraints",
  "status": "in_progress",
  "priority": "medium",
  "project_id": "uuid",
  "assignee_id": "uuid",
  "creator_id": "uuid",
  "due_date": "2026-04-20",
  "created_at": "2026-04-10T00:00:00Z",
  "updated_at": "2026-04-10T01:00:00Z"
}
```

4. `DELETE /tasks/{task_id}`
- Response `204` (no body)

### Error Contract
- `400`
```json
{ "error": "validation failed", "fields": { "field_name": "reason" } }
```
- `401`
```json
{ "error": "unauthorized" }
```
- `403`
```json
{ "error": "forbidden" }
```
- `404`
```json
{ "error": "not found" }
```

## 7. What You’d Do With More Time
- Add comprehensive automated tests for auth, permissions, filtering, pagination boundaries, and stats edge cases.
- Add role-based access and clearer collaborator membership management at the project level.
- Add API-level rate limiting and token rotation/refresh strategy.
- Add CI pipeline (lint, tests, migration check) for every PR.
- Add richer OpenAPI examples for every endpoint and error case.

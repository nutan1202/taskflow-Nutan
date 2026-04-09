# TaskFlow (backend-only)

FastAPI + PostgreSQL task management API.

## 1. Overview

<!-- What this is, stack -->

## 2. Architecture decisions

<!-- Why this structure, tradeoffs -->

## 3. Environment files

Two environment example files are used intentionally:

- `.env.example` (repo root): Docker Compose + container runtime variables.
- `backend/.env.backend.example`: backend-only local run (without Compose).

## 4. Running locally (Docker Compose)

```bash
git clone <your-repo-url>
cd taskflow-<your-name>
cp .env.example .env
docker compose up --build
```

API base URL: `http://localhost:8000` (adjust if `API_PUBLISH_PORT` is set).

## 5. Running backend directly (without Compose)

```bash
cd backend
cp .env.backend.example .env
# Start your local postgres first, then run the API
```

## 6. Running migrations

Migrations run automatically on API container startup. To run manually inside the API container:

```bash
docker compose exec api alembic upgrade head
```

## 7. Test credentials

```
Email:    admin@example.com
Password: ChangeMe123!
```

## 8. API reference

<!-- Endpoints or link to Postman/Bruno collection -->

## 9. What you'd do with more time

<!-- Honest reflection -->

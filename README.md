# TaskFlow (backend-only)

FastAPI + PostgreSQL task management API. See sections below (assignment template).

## 1. Overview

<!-- What this is, stack -->

## 2. Architecture decisions

<!-- Why this structure, tradeoffs -->

## 3. Running locally

```bash
git clone <your-repo-url>
cd taskflow-<your-name>
cp .env.example .env
docker compose up --build
```

API base URL: `http://localhost:8000` (adjust if `API_PUBLISH_PORT` is set).

## 4. Running migrations

Migrations run automatically on API container startup. To run manually inside the API container:

```bash
docker compose exec api alembic upgrade head
```

## 5. Test credentials

<!-- After seed is implemented -->

```
Email:    test@example.com
Password: password123
```

## 6. API reference

<!-- Endpoints or link to Postman/Bruno collection -->

## 7. What you'd do with more time

<!-- Honest reflection -->

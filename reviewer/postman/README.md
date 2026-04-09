# Reviewer API Collection (Postman)

## Files
- `TaskFlow.postman_collection.json`
- `TaskFlow.local.postman_environment.json`

## Quick Use
1. Start backend:
   - `cp .env.example .env`
   - `docker compose up --build`
2. Import both files into Postman.
3. Select environment: `TaskFlow Local`.
4. Run in order:
   - `Auth / Login` (auto-saves `token` and `user_id`)
   - `Projects / List Projects`
   - `Projects / Create Project` (auto-saves `project_id`)
   - `Tasks / Create Task` (auto-saves `task_id`)
   - remaining requests as needed

## Notes
- Seed credentials are preconfigured:
  - `test@example.com` / `password123`
- Includes bonus endpoint:
  - `GET /projects/{id}/stats`
- Includes filter and pagination examples:
  - `GET /projects?page=&limit=`
  - `GET /projects/{id}/tasks?status=&assignee=&page=&limit=`

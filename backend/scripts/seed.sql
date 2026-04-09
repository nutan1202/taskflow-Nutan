-- TaskFlow seed data (idempotent)
-- Creates:
-- 1 user (test@example.com / password123)
-- 1 project
-- 3 tasks with different statuses

BEGIN;

INSERT INTO users (id, name, email, password, created_at)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'Test User',
    'test@example.com',
    '$2b$12$YZfko1udeXPL64SvgmdPfewzpOek2T7vaHNeV8y7WmLRay3k/5J/i',
    NOW()
)
ON CONFLICT (email) DO NOTHING;

INSERT INTO projects (id, name, description, owner_id, created_at)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    'TaskFlow Demo Project',
    'Seeded project for reviewer testing',
    '11111111-1111-1111-1111-111111111111',
    NOW()
)
ON CONFLICT DO NOTHING;

INSERT INTO tasks (
    id,
    title,
    description,
    status,
    priority,
    project_id,
    assignee_id,
    creator_id,
    due_date,
    created_at,
    updated_at
)
VALUES
(
    '33333333-3333-3333-3333-333333333331',
    'Seed task: todo',
    'Initial task in todo state',
    'todo',
    'medium',
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    CURRENT_DATE + INTERVAL '3 day',
    NOW(),
    NOW()
),
(
    '33333333-3333-3333-3333-333333333332',
    'Seed task: in progress',
    'Task currently being worked on',
    'in_progress',
    'high',
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    CURRENT_DATE + INTERVAL '5 day',
    NOW(),
    NOW()
),
(
    '33333333-3333-3333-3333-333333333333',
    'Seed task: done',
    'Completed task example',
    'done',
    'low',
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    CURRENT_DATE + INTERVAL '1 day',
    NOW(),
    NOW()
)
ON CONFLICT DO NOTHING;

COMMIT;

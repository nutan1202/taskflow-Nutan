# SQLAlchemy 2.0 Models Documentation

## Overview

This document explains the database models, indexes, constraints, and delete behavior for the TaskFlow application.

## Models

### 1. User Model (`app/models/user.py`)

Represents application users who can own projects, create tasks, and be assigned tasks.

**Fields:**
- `id` (UUID): Primary key, auto-generated
- `name` (String): User's full name (required)
- `email` (String): Unique email address for login (required)
- `password` (String): Hashed password (required)
- `created_at` (DateTime): Timezone-aware timestamp of user registration

**Relationships:**
- `owned_projects`: One-to-many with Project (cascade delete)
- `assigned_tasks`: One-to-many with Task (assignee)
- `created_tasks`: One-to-many with Task (creator)

---

### 2. Project Model (`app/models/project.py`)

Represents a project that contains multiple tasks and is owned by a user.

**Fields:**
- `id` (UUID): Primary key, auto-generated
- `name` (String): Project name (required)
- `description` (Text): Optional project description
- `owner_id` (UUID): Foreign key to User (required)
- `created_at` (DateTime): Timezone-aware timestamp of project creation

**Relationships:**
- `owner`: Many-to-one with User
- `tasks`: One-to-many with Task (cascade delete)

---

### 3. Task Model (`app/models/task.py`)

Represents a work item within a project with status tracking and assignment capabilities.

**Fields:**
- `id` (UUID): Primary key, auto-generated
- `title` (String): Task title (required)
- `description` (Text): Optional detailed description
- `status` (Enum): Task status - `todo`, `in_progress`, or `done` (default: `todo`)
- `priority` (Enum): Task priority - `low`, `medium`, or `high` (default: `medium`)
- `project_id` (UUID): Foreign key to Project (required)
- `assignee_id` (UUID): Foreign key to User (nullable)
- `creator_id` (UUID): Foreign key to User (required)
- `due_date` (Date): Optional due date
- `created_at` (DateTime): Timezone-aware timestamp of task creation
- `updated_at` (DateTime): Timezone-aware timestamp of last update (auto-updated)

**Relationships:**
- `project`: Many-to-one with Project
- `assignee`: Many-to-one with User (optional)
- `creator`: Many-to-one with User (required)

**Enums:**
- `TaskStatus`: `TODO`, `IN_PROGRESS`, `DONE`
- `TaskPriority`: `LOW`, `MEDIUM`, `HIGH`

---

## Indexes

### User Indexes

1. **`ix_users_email`** (email)
   - **Purpose**: Fast lookup for login authentication and email uniqueness checks
   - **Query Pattern**: `WHERE email = ?`

2. **`ix_users_created_at`** (created_at)
   - **Purpose**: Sorting and filtering users by registration date
   - **Query Pattern**: `ORDER BY created_at DESC`

### Project Indexes

1. **`ix_projects_owner_id`** (owner_id)
   - **Purpose**: Fast retrieval of all projects owned by a specific user
   - **Query Pattern**: `WHERE owner_id = ?`

2. **`ix_projects_created_at`** (created_at)
   - **Purpose**: Sorting projects by creation date
   - **Query Pattern**: `ORDER BY created_at DESC`

3. **`ix_projects_owner_id_created_at`** (owner_id, created_at)
   - **Purpose**: Composite index for retrieving a user's projects sorted by date
   - **Query Pattern**: `WHERE owner_id = ? ORDER BY created_at DESC`

### Task Indexes

#### Single Column Indexes

1. **`ix_tasks_project_id`** (project_id)
   - **Purpose**: Retrieve all tasks in a project
   - **Query Pattern**: `WHERE project_id = ?`

2. **`ix_tasks_assignee_id`** (assignee_id)
   - **Purpose**: Retrieve all tasks assigned to a user
   - **Query Pattern**: `WHERE assignee_id = ?`

3. **`ix_tasks_creator_id`** (creator_id)
   - **Purpose**: Permission checks and filtering tasks by creator
   - **Query Pattern**: `WHERE creator_id = ?`
   - **Permission Use**: Critical for delete permission checks

4. **`ix_tasks_status`** (status)
   - **Purpose**: Filter tasks by status across all projects
   - **Query Pattern**: `WHERE status = ?`

5. **`ix_tasks_priority`** (priority)
   - **Purpose**: Filter tasks by priority
   - **Query Pattern**: `WHERE priority = ?`

6. **`ix_tasks_due_date`** (due_date)
   - **Purpose**: Find tasks by due date or overdue tasks
   - **Query Pattern**: `WHERE due_date <= ? ORDER BY due_date`

7. **`ix_tasks_created_at`** (created_at)
   - **Purpose**: Sort tasks by creation date
   - **Query Pattern**: `ORDER BY created_at DESC`

8. **`ix_tasks_updated_at`** (updated_at)
   - **Purpose**: Sort tasks by last modification
   - **Query Pattern**: `ORDER BY updated_at DESC`

#### Composite Indexes

1. **`ix_tasks_project_id_status`** (project_id, status)
   - **Purpose**: Filter project tasks by status (e.g., show all "in_progress" tasks in a project)
   - **Query Pattern**: `WHERE project_id = ? AND status = ?`

2. **`ix_tasks_project_id_assignee_id`** (project_id, assignee_id)
   - **Purpose**: Find tasks assigned to a specific user within a project
   - **Query Pattern**: `WHERE project_id = ? AND assignee_id = ?`

3. **`ix_tasks_assignee_id_status`** (assignee_id, status)
   - **Purpose**: User's task dashboard filtered by status
   - **Query Pattern**: `WHERE assignee_id = ? AND status = ?`

4. **`ix_tasks_project_id_due_date`** (project_id, due_date)
   - **Purpose**: Project tasks sorted by due date
   - **Query Pattern**: `WHERE project_id = ? ORDER BY due_date`

5. **`ix_tasks_assignee_id_due_date`** (assignee_id, due_date)
   - **Purpose**: User's assigned tasks sorted by due date
   - **Query Pattern**: `WHERE assignee_id = ? ORDER BY due_date`

---

## Constraints

### Primary Keys
- All tables use UUID primary keys for better distribution and security
- UUIDs are generated by the application (not database) for better control

### Foreign Keys

1. **Project.owner_id → User.id**
   - Constraint: `NOT NULL`
   - Every project must have an owner

2. **Task.project_id → Project.id**
   - Constraint: `NOT NULL`
   - Every task must belong to a project

3. **Task.assignee_id → User.id**
   - Constraint: `NULL` allowed
   - Tasks can be unassigned

4. **Task.creator_id → User.id**
   - Constraint: `NOT NULL`
   - Every task must have a creator (required for permission checks)

### Unique Constraints

1. **User.email**
   - Ensures email uniqueness across all users
   - Prevents duplicate accounts

### Check Constraints (via Enums)

1. **Task.status**
   - Must be one of: `todo`, `in_progress`, `done`

2. **Task.priority**
   - Must be one of: `low`, `medium`, `high`

---

## Delete Behavior & Cascades

### User Deletion

**When a user is deleted:**

1. **Owned Projects** → `CASCADE DELETE`
   - All projects owned by the user are deleted
   - This triggers cascade deletion of all tasks in those projects
   - **Rationale**: Projects are owned resources; without an owner, they become orphaned

2. **Created Tasks** → `CASCADE DELETE`
   - All tasks created by the user are deleted
   - **Rationale**: Task creator is required for permission checks; orphaned tasks would break the permission model

3. **Assigned Tasks** → `SET NULL`
   - Tasks assigned to the user have `assignee_id` set to NULL
   - Tasks remain in the system but become unassigned
   - **Rationale**: Task assignment is optional; tasks can exist without an assignee

**Impact:**
- Deleting a user is a destructive operation
- Consider implementing soft deletes or transfer ownership features in production
- Application should warn users before deletion

### Project Deletion

**When a project is deleted:**

1. **Tasks** → `CASCADE DELETE`
   - All tasks in the project are deleted
   - **Rationale**: Tasks cannot exist without a parent project

**Impact:**
- Deleting a project removes all associated tasks
- Application should implement confirmation dialogs
- Consider archiving instead of hard deletion

### Task Deletion

**When a task is deleted:**
- No cascading effects (tasks are leaf nodes in the hierarchy)
- Foreign key references are simply removed

---

## Permission Implications

### Task Creator Field (`creator_id`)

The `creator_id` field is **critical** for implementing proper authorization:

1. **Delete Permission**
   - Only the task creator should be able to delete a task
   - Check: `task.creator_id == current_user.id`

2. **Edit Permission**
   - Task creator typically has full edit rights
   - Project owner may also have edit rights
   - Check: `task.creator_id == current_user.id OR task.project.owner_id == current_user.id`

3. **Audit Trail**
   - Tracks who created each task
   - Useful for accountability and reporting

4. **Cascade Behavior**
   - When creator is deleted, their tasks are also deleted
   - This prevents orphaned tasks with no creator
   - Alternative: Transfer tasks to project owner before user deletion

### Project Owner Field (`owner_id`)

1. **Full Control**
   - Project owner has full control over the project and all its tasks
   - Can delete project (which cascades to all tasks)

2. **Delegation**
   - Owner can assign tasks to other users
   - Assignees can work on tasks but may have limited permissions

---

## Timezone Handling

All timestamp fields use **timezone-aware** datetime objects:

- `DateTime(timezone=True)` in SQLAlchemy
- Defaults to UTC: `datetime.now(timezone.utc)`
- PostgreSQL stores as `TIMESTAMP WITH TIME ZONE`

**Benefits:**
- Consistent time representation across different timezones
- Proper sorting and comparison
- Client applications can convert to local timezone for display

---

## Best Practices

### 1. UUID Generation
- UUIDs are generated by the application (Python's `uuid.uuid4()`)
- `server_default=None` prevents database-side generation
- Allows knowing the ID before database insertion

### 2. Enum Storage
- `native_enum=False` stores enums as VARCHAR in PostgreSQL
- More flexible for migrations and changes
- Avoids PostgreSQL ENUM type limitations

### 3. Relationship Loading
- Use `lazy="select"` (default) for most relationships
- Consider `lazy="joined"` for frequently accessed relationships
- Use `selectinload()` or `joinedload()` in queries for optimization

### 4. Index Strategy
- Single-column indexes for simple filters
- Composite indexes for common multi-column queries
- Index order matters: most selective column first
- Monitor query performance and adjust indexes accordingly

### 5. Migration Strategy
- Use Alembic for schema migrations
- Test migrations on a copy of production data
- Always create down migrations for rollback capability
- Document breaking changes

---

## Example Queries

### Get user's projects with task counts
```python
from sqlalchemy import select, func
from app.models import User, Project, Task

stmt = (
    select(Project, func.count(Task.id).label("task_count"))
    .join(Project.owner)
    .outerjoin(Project.tasks)
    .where(User.id == user_id)
    .group_by(Project.id)
    .order_by(Project.created_at.desc())
)
```

### Get user's assigned tasks by status
```python
stmt = (
    select(Task)
    .where(Task.assignee_id == user_id)
    .where(Task.status == TaskStatus.IN_PROGRESS)
    .order_by(Task.due_date.asc())
)
# Uses index: ix_tasks_assignee_id_status
```

### Get overdue tasks in a project
```python
from datetime import date

stmt = (
    select(Task)
    .where(Task.project_id == project_id)
    .where(Task.due_date < date.today())
    .where(Task.status != TaskStatus.DONE)
    .order_by(Task.due_date.asc())
)
# Uses index: ix_tasks_project_id_due_date
```

### Check if user can delete a task
```python
def can_delete_task(task: Task, user: User) -> bool:
    """Check if user has permission to delete a task."""
    # Task creator can delete
    if task.creator_id == user.id:
        return True
    
    # Project owner can delete any task in their project
    if task.project.owner_id == user.id:
        return True
    
    return False
```

---

## Summary

The models are designed with:
- ✅ PostgreSQL UUID primary keys
- ✅ Timezone-aware timestamps
- ✅ Proper foreign key relationships
- ✅ Strategic indexes for common queries
- ✅ Appropriate cascade behaviors
- ✅ Permission-aware design (creator_id)
- ✅ SQLAlchemy 2.0 modern syntax
- ✅ Type hints for better IDE support
- ✅ No auto-migration logic (use Alembic)

The schema supports a robust task management system with proper data integrity, performance optimization, and security considerations.

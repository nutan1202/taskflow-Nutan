# Alembic Migration Guide - Initial Schema

## Overview

This document explains the initial database migration (`0001_initial`) for the TaskFlow application, including upgrade steps, downgrade steps, and PostgreSQL-specific considerations.

## Migration File

**Location**: `alembic/versions/0001_initial_placeholder.py`

**Revision ID**: `0001_initial`

**Revises**: `None` (initial migration)

---

## Upgrade Steps

The `upgrade()` function creates the complete database schema in the following order:

### Step 1: Create PostgreSQL ENUM Types

```python
task_status_enum = postgresql.ENUM(
    'todo', 'in_progress', 'done',
    name='task_status',
    create_type=True
)
task_status_enum.create(op.get_bind())

task_priority_enum = postgresql.ENUM(
    'low', 'medium', 'high',
    name='task_priority',
    create_type=True
)
task_priority_enum.create(op.get_bind())
```

**What happens:**
- Creates two PostgreSQL ENUM types at the database level
- `task_status`: Defines valid task statuses (todo, in_progress, done)
- `task_priority`: Defines valid task priorities (low, medium, high)
- These must be created BEFORE the tables that use them

**Why first:**
- PostgreSQL requires ENUM types to exist before they can be referenced in table columns
- Creating them first ensures proper dependency order

---

### Step 2: Create Users Table

```python
op.create_table(
    'users',
    sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.UniqueConstraint('email', name='uq_users_email'),
)
```

**What happens:**
- Creates the `users` table with UUID primary key
- All fields are required (nullable=False)
- Email has a unique constraint to prevent duplicate accounts
- `created_at` uses timezone-aware datetime (TIMESTAMP WITH TIME ZONE in PostgreSQL)

**Indexes created:**
- `ix_users_email`: Fast lookup for login and uniqueness checks
- `ix_users_created_at`: Sorting users by registration date

**Why second:**
- Users table has no foreign key dependencies
- Other tables (projects, tasks) reference users, so it must exist first

---

### Step 3: Create Projects Table

```python
op.create_table(
    'projects',
    sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(
        ['owner_id'], 
        ['users.id'],
        name='fk_projects_owner_id_users',
        ondelete='CASCADE'
    ),
)
```

**What happens:**
- Creates the `projects` table with UUID primary key
- `description` is optional (nullable=True)
- `owner_id` is a required foreign key to `users.id`
- **CASCADE DELETE**: When a user is deleted, all their projects are deleted

**Indexes created:**
- `ix_projects_owner_id`: Fast retrieval of user's projects
- `ix_projects_created_at`: Sorting projects by creation date
- `ix_projects_owner_id_created_at`: Composite index for user's projects sorted by date

**Why third:**
- Depends on `users` table (foreign key to users.id)
- Tasks table depends on projects, so it must exist before tasks

---

### Step 4: Create Tasks Table

```python
op.create_table(
    'tasks',
    sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', task_status_enum, nullable=False, server_default='todo'),
    sa.Column('priority', task_priority_enum, nullable=False, server_default='medium'),
    sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('assignee_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    # ... foreign key constraints
)
```

**What happens:**
- Creates the `tasks` table with UUID primary key
- Uses the previously created ENUM types for status and priority
- `server_default='todo'` and `server_default='medium'` provide database-level defaults
- Three foreign keys with different cascade behaviors:
  - `project_id` → `projects.id` (CASCADE DELETE)
  - `assignee_id` → `users.id` (SET NULL) - nullable
  - `creator_id` → `users.id` (CASCADE DELETE) - required

**Foreign Key Cascade Behaviors:**

1. **project_id (CASCADE DELETE)**
   - When a project is deleted, all its tasks are deleted
   - Rationale: Tasks cannot exist without a parent project

2. **assignee_id (SET NULL)**
   - When an assigned user is deleted, tasks are unassigned (assignee_id = NULL)
   - Rationale: Tasks can exist without an assignee

3. **creator_id (CASCADE DELETE)**
   - When a task creator is deleted, their tasks are deleted
   - Rationale: Creator is required for permission checks; orphaned tasks would break authorization

**Indexes created:**

*Single-column indexes:*
- `ix_tasks_project_id`: Filter tasks by project
- `ix_tasks_assignee_id`: Filter tasks by assignee
- `ix_tasks_creator_id`: Permission checks and filtering by creator
- `ix_tasks_status`: Filter by status
- `ix_tasks_priority`: Filter by priority
- `ix_tasks_due_date`: Filter/sort by due date
- `ix_tasks_created_at`: Sort by creation date
- `ix_tasks_updated_at`: Sort by last update

*Composite indexes:*
- `ix_tasks_project_id_status`: Project tasks filtered by status
- `ix_tasks_project_id_assignee_id`: Project tasks by assignee
- `ix_tasks_assignee_id_status`: User's tasks filtered by status
- `ix_tasks_project_id_due_date`: Project tasks sorted by due date
- `ix_tasks_assignee_id_due_date`: User's tasks sorted by due date

**Why last:**
- Depends on both `users` and `projects` tables
- Leaf node in the dependency graph

---

## Downgrade Steps

The `downgrade()` function removes the schema in reverse order:

### Step 1: Drop Tasks Table

```python
op.drop_table('tasks')
```

**What happens:**
- Drops the `tasks` table
- All indexes on the table are automatically dropped
- All foreign key constraints are automatically removed

**Why first:**
- Tasks depend on projects and users
- Must be dropped before its dependencies

---

### Step 2: Drop Projects Table

```python
op.drop_table('projects')
```

**What happens:**
- Drops the `projects` table
- All indexes are automatically dropped
- Foreign key to users is automatically removed

**Why second:**
- Projects depend on users
- Must be dropped before users

---

### Step 3: Drop Users Table

```python
op.drop_table('users')
```

**What happens:**
- Drops the `users` table
- All indexes are automatically dropped
- No foreign key dependencies remain

**Why third:**
- No dependencies on other tables
- Can be safely dropped after projects and tasks

---

### Step 4: Drop ENUM Types

```python
op.execute('DROP TYPE IF EXISTS task_priority')
op.execute('DROP TYPE IF EXISTS task_status')
```

**What happens:**
- Explicitly drops the PostgreSQL ENUM types
- Uses `IF EXISTS` to prevent errors if types don't exist
- Uses raw SQL because Alembic doesn't have a built-in method for this

**Why last:**
- ENUM types were created first, so they're dropped last
- Must be dropped AFTER all tables that use them
- PostgreSQL won't allow dropping ENUMs that are still in use

---

## PostgreSQL ENUM Handling - Important Caveats

### 1. ENUM Creation

**Method used:**
```python
task_status_enum = postgresql.ENUM(
    'todo', 'in_progress', 'done',
    name='task_status',
    create_type=True
)
task_status_enum.create(op.get_bind())
```

**Why this approach:**
- Explicit control over ENUM creation
- Clear separation between type creation and table creation
- Works reliably across PostgreSQL versions

**Alternative (not used):**
```python
# This would create the ENUM implicitly when creating the table
sa.Column('status', sa.Enum('todo', 'in_progress', 'done', name='task_status'))
```

**Why we avoid the alternative:**
- Less explicit
- Harder to control when ENUM is created
- Can cause issues with multiple tables using the same ENUM

---

### 2. ENUM Modification Limitations

**Important:** PostgreSQL ENUMs are **immutable** once created. You cannot:
- Add new values to an existing ENUM (requires workaround)
- Remove values from an ENUM
- Rename ENUM values
- Reorder ENUM values

**Workaround for adding values:**
```sql
-- Must use raw SQL in a migration
ALTER TYPE task_status ADD VALUE 'archived' AFTER 'done';
```

**Better approach for future flexibility:**
- Use VARCHAR with CHECK constraints instead of ENUMs
- This is why the models use `native_enum=False`
- Allows easier modifications in future migrations

**Current implementation:**
```python
# In models, we use:
Enum(TaskStatus, name="task_status", native_enum=False)
```

This stores enum values as VARCHAR in the database, making future changes easier.

---

### 3. ENUM Deletion

**Critical:** ENUMs must be dropped AFTER all tables using them.

**Correct order (as in migration):**
```python
def downgrade():
    op.drop_table('tasks')      # Drop table using ENUMs
    op.drop_table('projects')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS task_priority')  # Then drop ENUMs
    op.execute('DROP TYPE IF EXISTS task_status')
```

**Incorrect order (will fail):**
```python
def downgrade():
    op.execute('DROP TYPE task_status')  # ERROR: type is still in use
    op.drop_table('tasks')
```

**Error you'd see:**
```
ERROR: cannot drop type task_status because other objects depend on it
DETAIL: column status of table tasks depends on type task_status
```

---

### 4. ENUM Type Naming

**Convention used:**
- ENUM type name: `task_status` (snake_case, singular)
- Python enum class: `TaskStatus` (PascalCase)
- Column name: `status` (snake_case)

**Why explicit naming:**
```python
postgresql.ENUM(..., name='task_status')
```

- Prevents Alembic from auto-generating random names
- Makes migrations reproducible
- Easier to debug and maintain

---

### 5. Server Defaults with ENUMs

**Implementation:**
```python
sa.Column('status', task_status_enum, nullable=False, server_default='todo')
```

**Important notes:**
- `server_default` must be a string literal matching an ENUM value
- The default is enforced at the database level
- Application-level defaults (in models) are separate

**Both levels of defaults:**
```python
# Database level (migration)
server_default='todo'

# Application level (model)
default=TaskStatus.TODO
```

**Why both:**
- Database default: Ensures data integrity even with raw SQL inserts
- Application default: Provides default when creating objects in Python

---

### 6. ENUM Values Must Match

**Critical:** ENUM values in migration must match model definitions.

**Migration:**
```python
postgresql.ENUM('todo', 'in_progress', 'done', name='task_status')
```

**Model:**
```python
class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
```

**Mismatch example (will cause errors):**
```python
# Migration has: 'todo', 'in_progress', 'done'
# Model has: 'TODO', 'IN_PROGRESS', 'DONE'  # WRONG - case mismatch
```

---

## Running the Migration

### Upgrade to latest

```bash
# From backend directory
alembic upgrade head
```

**What happens:**
1. Alembic checks current database version
2. Runs all pending migrations (in this case, just 0001_initial)
3. Creates all tables, indexes, and constraints
4. Updates alembic_version table

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial, Initial schema migration for TaskFlow.
```

---

### Downgrade (rollback)

```bash
# Rollback to base (empty database)
alembic downgrade base
```

**What happens:**
1. Runs downgrade() function
2. Drops all tables in reverse order
3. Drops ENUM types
4. Updates alembic_version table

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade 0001_initial -> , Initial schema migration for TaskFlow.
```

---

### Check current version

```bash
alembic current
```

**Output if migrated:**
```
0001_initial (head)
```

**Output if not migrated:**
```
(no current revision)
```

---

### View migration history

```bash
alembic history
```

**Output:**
```
0001_initial -> <head>, Initial schema migration for TaskFlow.
```

---

## Verification Queries

After running the migration, verify the schema:

### Check tables exist

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

**Expected output:**
```
 table_name 
------------
 projects
 tasks
 users
```

---

### Check ENUM types

```sql
SELECT typname, typtype 
FROM pg_type 
WHERE typtype = 'e';
```

**Expected output:**
```
    typname     | typtype 
----------------+---------
 task_priority  | e
 task_status    | e
```

---

### Check ENUM values

```sql
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = 'task_status'::regtype 
ORDER BY enumsortorder;
```

**Expected output:**
```
  enumlabel  
-------------
 todo
 in_progress
 done
```

---

### Check indexes

```sql
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;
```

**Expected output includes:**
```
           indexname            | tablename 
--------------------------------+-----------
 ix_projects_created_at         | projects
 ix_projects_owner_id           | projects
 ix_projects_owner_id_created_at| projects
 ix_tasks_assignee_id           | tasks
 ix_tasks_assignee_id_due_date  | tasks
 ix_tasks_assignee_id_status    | tasks
 ...
```

---

### Check foreign keys

```sql
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name, kcu.column_name;
```

**Expected output:**
```
 table_name | column_name | foreign_table_name | foreign_column_name | delete_rule 
------------+-------------+--------------------+---------------------+-------------
 projects   | owner_id    | users              | id                  | CASCADE
 tasks      | assignee_id | users              | id                  | SET NULL
 tasks      | creator_id  | users              | id                  | CASCADE
 tasks      | project_id  | projects           | id                  | CASCADE
```

---

## Troubleshooting

### Error: "type already exists"

**Problem:**
```
ERROR: type "task_status" already exists
```

**Solution:**
```bash
# Either drop the type manually:
psql -d taskflow -c "DROP TYPE IF EXISTS task_status CASCADE;"

# Or run downgrade first:
alembic downgrade base
alembic upgrade head
```

---

### Error: "relation already exists"

**Problem:**
```
ERROR: relation "users" already exists
```

**Solution:**
```bash
# Check if migration was already run:
alembic current

# If it shows 0001_initial, the migration is already applied
# If you want to reapply, downgrade first:
alembic downgrade base
alembic upgrade head
```

---

### Error: "cannot drop type because other objects depend on it"

**Problem:**
```
ERROR: cannot drop type task_status because other objects depend on it
```

**Solution:**
This means tables using the ENUM still exist. Drop tables first:
```sql
DROP TABLE IF EXISTS tasks CASCADE;
DROP TYPE IF EXISTS task_status;
```

Or use the migration downgrade:
```bash
alembic downgrade base
```

---

## Summary

### Upgrade Order
1. ✅ Create ENUM types (task_status, task_priority)
2. ✅ Create users table + indexes
3. ✅ Create projects table + indexes + foreign key to users
4. ✅ Create tasks table + indexes + foreign keys to users and projects

### Downgrade Order
1. ✅ Drop tasks table (and its indexes/constraints)
2. ✅ Drop projects table (and its indexes/constraints)
3. ✅ Drop users table (and its indexes/constraints)
4. ✅ Drop ENUM types (task_priority, task_status)

### Key Features
- ✅ Explicit, readable migration (not autogenerated noise)
- ✅ Complete upgrade and downgrade functions
- ✅ PostgreSQL-specific UUID and ENUM types
- ✅ Proper cascade behaviors (CASCADE, SET NULL)
- ✅ Comprehensive indexes for query performance
- ✅ Named constraints for better debugging
- ✅ Timezone-aware timestamps

### PostgreSQL ENUM Caveats
- ⚠️ ENUMs are immutable (can't easily modify values)
- ⚠️ Must create ENUMs before tables that use them
- ⚠️ Must drop tables before dropping ENUMs
- ⚠️ Use `native_enum=False` in models for flexibility
- ⚠️ ENUM values must match exactly between migration and models

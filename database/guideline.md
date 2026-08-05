# SQLAlchemy + Alembic Database Workflow

## Initial Setup (One Time)

### 1. Install Alembic

```bash
pip install alembic
```

---

### 2. Initialize Alembic

```bash
alembic init migrations
```

This creates:

```text
migrations/
├── env.py
├── script.py.mako
└── versions/

alembic.ini
```

---

### 3. Configure `migrations/env.py`

```python
from database.models.base_class import Base
import database.models

from database.session import DATABASE_URL

config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata
```

Ensure `database/models/__init__.py` imports all of your models.

---

### 4. Generate the Initial Migration

```bash
alembic revision --autogenerate -m "initial schema"
```

---

### 5. Review the Generated Migration

Open:

```text
migrations/
└── versions/
    └── <revision>_initial_schema.py
```

Verify that `upgrade()` contains the expected `op.create_table(...)` statements.

---

### 6. Apply the Migration

```bash
alembic upgrade head
```

Your database schema is now created.

---

# Initial Setup Flow

```text
Create Models
      │
      ▼
pip install alembic
      │
      ▼
alembic init migrations
      │
      ▼
Configure migrations/env.py
      │
      ▼
Generate Initial Migration
      │
      ▼
alembic revision --autogenerate -m "initial schema"
      │
      ▼
Review Migration
      │
      ▼
Apply Migration
      │
      ▼
alembic upgrade head
      │
      ▼
Database Ready
```

---

# Daily Development Workflow

Whenever you add, remove, or modify a model:

```text
Modify SQLAlchemy Models
        │
        ▼
Generate Migration
        │
        ▼
alembic revision --autogenerate -m "<migration message>"
        │
        ▼
Review Generated Migration
        │
        ▼
Apply Migration
        │
        ▼
alembic upgrade head
        │
        ▼
Continue Development
```

---

# Example: Adding a Column

```text
Add field to UserModel
        │
        ▼
alembic revision --autogenerate -m "add bio column"
        │
        ▼
Review generated migration
        │
        ▼
alembic upgrade head
```

Commands:

```bash
alembic revision --autogenerate -m "add bio column"
alembic upgrade head
```

---

# Example: Removing a Column

```text
Remove field from UserModel
        │
        ▼
alembic revision --autogenerate -m "remove old field"
        │
        ▼
Review generated migration
        │
        ▼
alembic upgrade head
```

Commands:

```bash
alembic revision --autogenerate -m "remove old field"
alembic upgrade head
```

---

# Example: Creating a New Table

```text
Create New SQLAlchemy Model
        │
        ▼
alembic revision --autogenerate -m "create commits table"
        │
        ▼
Review generated migration
        │
        ▼
alembic upgrade head
```

Commands:

```bash
alembic revision --autogenerate -m "create commits table"
alembic upgrade head
```

---

# Useful Alembic Commands

Generate a migration:

```bash
alembic revision --autogenerate -m "<message>"
```

Apply all pending migrations:

```bash
alembic upgrade head
```

Upgrade to a specific revision:

```bash
alembic upgrade <revision_id>
```

Downgrade one migration:

```bash
alembic downgrade -1
```

Downgrade to a specific revision:

```bash
alembic downgrade <revision_id>
```

Downgrade everything:

```bash
alembic downgrade base
```

Show current database version:

```bash
alembic current
```

Show migration history:

```bash
alembic history
```

Show pending SQL without executing it:

```bash
alembic upgrade head --sql
```

Create an empty migration for manual SQL:

```bash
alembic revision -m "add pgvector extension"
```

---

# Recommended Rule

> **Never manually edit the database schema.**
>
> Make changes to your SQLAlchemy models first, let Alembic generate the migration, review it, and then apply it using `alembic upgrade head`.
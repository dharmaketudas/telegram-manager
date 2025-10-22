# Database Migrations System

## Overview

This directory contains database migration files for the Telegram Contact Manager. The migration system ensures that database schema changes are tracked, versioned, and applied consistently across all environments.

## How It Works

### Migration Tracking

- Each migration is tracked in the `_migrations` table
- Migrations are identified by a unique version number (e.g., "001", "002", "003")
- Once applied, a migration is never run again
- Migrations can be applied in any order (though sequential is recommended)

### Migration Files

Each migration file follows this naming convention:
```
migration_XXX_description.py
```

Where:
- `XXX` is a 3-digit version number (001, 002, 003, etc.)
- `description` is a brief, lowercase name with underscores

Examples:
- `migration_001_initial_schema.py`
- `migration_002_add_user_preferences.py`
- `migration_003_add_message_status.py`

## Creating a New Migration

### Step 1: Create the Migration File

Create a new file in this directory:

```python
# migration_002_add_user_preferences.py
"""
Migration 002: Add User Preferences
Adds a user_preferences table for storing user settings
"""

import logging
from . import Migration
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class AddUserPreferencesMigration(Migration):
    """Add user preferences table"""

    def __init__(self):
        super().__init__(
            version="002",
            name="add_user_preferences",
            description="Add user_preferences table for storing user settings"
        )

    async def up(self, db: DatabaseConnection):
        """Apply the migration"""
        logger.info("Adding user_preferences table...")

        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, preference_key)
            );
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id 
            ON user_preferences(user_id);
        """)

        await db.commit()
        logger.info("✓ User preferences table added successfully")

    async def down(self, db: DatabaseConnection):
        """Rollback the migration"""
        logger.warning("Removing user_preferences table...")

        await db.execute("DROP TABLE IF EXISTS user_preferences")
        await db.commit()

        logger.warning("✓ User preferences table removed")
```

### Step 2: Register the Migration

Edit `__init__.py` in this directory and add your migration to the imports and registration:

```python
# In the run_migrations() function, add:
from . import migration_002_add_user_preferences

# Register the migration
manager.register_migration(migration_002_add_user_preferences.AddUserPreferencesMigration())
```

### Step 3: Run Migrations

Start your application normally. The migration system will:
1. Detect the new migration
2. Check if it has been applied
3. Run it automatically if it hasn't been applied yet

Or manually run migrations:

```bash
cd backend
source venv/bin/activate
python -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from database import get_database, run_migrations

async def main():
    db = get_database()
    await db.connect()
    await run_migrations(db)
    await db.disconnect()

asyncio.run(main())
"
```

## Migration Best Practices

### 1. Keep Migrations Small and Focused

Each migration should do ONE thing:
- ✅ Add a single table
- ✅ Add an index
- ✅ Modify a column
- ❌ Add multiple unrelated tables in one migration

### 2. Always Use IF NOT EXISTS

Protect against partial failures:

```python
await db.execute("CREATE TABLE IF NOT EXISTS ...")
await db.execute("CREATE INDEX IF NOT EXISTS ...")
```

### 3. Test Both up() and down()

Always test:
- Applying the migration (up)
- Rolling it back (down)
- Reapplying it after rollback

### 4. Handle Data Migrations Carefully

When migrating data:
- Log progress for large datasets
- Use transactions
- Handle errors gracefully
- Provide rollback logic

Example:
```python
async def up(self, db: DatabaseConnection):
    # Add new column
    await db.execute("ALTER TABLE contacts ADD COLUMN verified BOOLEAN DEFAULT 0")
    
    # Migrate existing data in batches
    offset = 0
    batch_size = 1000
    
    while True:
        rows = await db.fetch_all(
            f"SELECT id FROM contacts LIMIT {batch_size} OFFSET {offset}"
        )
        
        if not rows:
            break
            
        # Process batch
        for row in rows:
            # Update based on business logic
            await db.execute(
                "UPDATE contacts SET verified = 1 WHERE id = ? AND phone IS NOT NULL",
                (row[0],)
            )
        
        offset += batch_size
        logger.info(f"Processed {offset} records...")
    
    await db.commit()
```

### 5. Document Your Migrations

Add clear comments explaining:
- What the migration does
- Why it's needed
- Any prerequisites
- Any manual steps required

### 6. Version Numbers

- Use 3-digit zero-padded numbers: 001, 002, 003, etc.
- Never reuse version numbers
- Keep versions sequential (but gaps are OK)
- Don't rename migration files after they've been applied

### 7. Never Modify Applied Migrations

Once a migration has been applied in any environment:
- ❌ Don't modify its code
- ❌ Don't delete it
- ✅ Create a new migration to make changes

## Migration Commands

### Check Migration Status

```python
from database import get_database, get_migration_status

async def check_status():
    db = get_database()
    await db.connect()
    
    status = await get_migration_status(db)
    
    for migration in status:
        applied = "✓" if migration['applied'] else "✗"
        print(f"{applied} {migration['version']} - {migration['name']}")
        if migration['applied']:
            print(f"  Applied: {migration['applied_at']}")
    
    await db.disconnect()
```

### Rollback Last Migration

```python
from database.migrations import get_migration_manager

async def rollback():
    db = get_database()
    await db.connect()
    
    manager = get_migration_manager(db)
    success = await manager.rollback_last_migration()
    
    if success:
        print("✓ Rollback successful")
    else:
        print("✗ Rollback failed")
    
    await db.disconnect()
```

## Troubleshooting

### Migration Failed Partway Through

If a migration fails:
1. Check the error logs
2. Fix the issue in the migration code
3. Manually clean up any partial changes in the database
4. The migration will retry on next startup

### Migration Marked as Applied But Isn't Complete

If a migration is marked as applied but didn't complete:

```sql
-- Remove the migration record
DELETE FROM _migrations WHERE version = '002';
```

Then restart the application to rerun it.

### Reset All Migrations (Development Only!)

**WARNING: This deletes all data!**

```python
from database import get_database, reset_database

async def reset():
    db = get_database()
    await db.connect()
    await reset_database(db)
    await db.disconnect()
```

## Migration File Template

Use this template for new migrations:

```python
"""
Migration XXX: Brief Description
Detailed description of what this migration does
"""

import logging
from . import Migration
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class YourMigrationName(Migration):
    """Brief description"""

    def __init__(self):
        super().__init__(
            version="XXX",  # 3-digit version number
            name="your_migration_name",
            description="Detailed description of the migration"
        )

    async def up(self, db: DatabaseConnection):
        """Apply the migration"""
        logger.info("Applying migration...")

        # Your migration code here
        await db.execute("""
            -- Your SQL here
        """)

        await db.commit()
        logger.info("✓ Migration applied successfully")

    async def down(self, db: DatabaseConnection):
        """Rollback the migration"""
        logger.warning("Rolling back migration...")

        # Your rollback code here
        await db.execute("""
            -- Your rollback SQL here
        """)

        await db.commit()
        logger.warning("✓ Migration rolled back successfully")
```

## Current Migrations

| Version | Name | Description | Status |
|---------|------|-------------|--------|
| 001 | initial_schema | Create base database schema | ✓ Applied |

## Additional Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Database Schema Overview](../README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Remember**: Migrations are permanent records of database changes. Treat them with care!
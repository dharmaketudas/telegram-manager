# Database Migrations - Quick Reference

## 🚀 Quick Commands

```bash
# Check migration status
python manage_migrations.py status

# Run pending migrations (automatic on app start)
python manage_migrations.py run

# Show database info
python manage_migrations.py info

# Rollback last migration
python manage_migrations.py rollback

# Reset database (⚠️ DELETES ALL DATA)
python manage_migrations.py reset
```

## 📝 Creating a New Migration

### 1. Create Migration File

```bash
cd src/database/migrations
nano migration_002_add_feature.py
```

### 2. Write Migration Code

```python
"""
Migration 002: Add Feature Name
Brief description of what this migration does
"""

import logging
from . import Migration
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class AddFeatureMigration(Migration):
    """Add feature description"""

    def __init__(self):
        super().__init__(
            version="002",  # INCREMENT from last migration
            name="add_feature",
            description="What this migration does"
        )

    async def up(self, db: DatabaseConnection):
        """Apply the migration"""
        logger.info("Applying migration...")

        # Create table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS new_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Add index
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_new_table_name
            ON new_table(name);
        """)

        await db.commit()
        logger.info("✓ Migration applied")

    async def down(self, db: DatabaseConnection):
        """Rollback the migration"""
        logger.warning("Rolling back migration...")

        await db.execute("DROP TABLE IF EXISTS new_table")
        await db.commit()

        logger.warning("✓ Rollback complete")
```

### 3. Register Migration

Edit `src/database/migrations/__init__.py`:

```python
def _register_all_migrations(manager: MigrationManager):
    from . import migration_001_initial_schema
    from . import migration_002_add_feature  # ADD THIS

    manager.register_migration(migration_001_initial_schema.InitialSchemaMigration())
    manager.register_migration(migration_002_add_feature.AddFeatureMigration())  # ADD THIS
```

### 4. Test Migration

```bash
# Check status (should show as pending)
python manage_migrations.py status

# Run the migration
python manage_migrations.py run

# Verify it worked
python manage_migrations.py info
```

## 🎯 Common Patterns

### Add a Table

```python
await db.execute("""
    CREATE TABLE IF NOT EXISTS table_name (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        field TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
```

### Add an Index

```python
await db.execute("""
    CREATE INDEX IF NOT EXISTS idx_table_field
    ON table_name(field);
""")
```

### Add a Column (SQLite)

```python
# Check if column exists first
cursor = await db.execute("PRAGMA table_info(table_name)")
columns = await cursor.fetchall()
column_names = [col[1] for col in columns]

if 'new_column' not in column_names:
    await db.execute("""
        ALTER TABLE table_name
        ADD COLUMN new_column TEXT;
    """)
```

### Add a Trigger

```python
await db.execute("""
    CREATE TRIGGER IF NOT EXISTS update_timestamp
    AFTER UPDATE ON table_name
    FOR EACH ROW
    BEGIN
        UPDATE table_name
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.id;
    END;
""")
```

### Data Migration (Batch Processing)

```python
# Get total count
result = await db.fetch_one("SELECT COUNT(*) FROM table_name")
total = result[0]

# Process in batches
batch_size = 100
for offset in range(0, total, batch_size):
    rows = await db.fetch_all(
        f"SELECT id, field FROM table_name LIMIT {batch_size} OFFSET {offset}"
    )
    
    for row in rows:
        # Process each row
        await db.execute(
            "UPDATE table_name SET new_field = ? WHERE id = ?",
            (transform(row[1]), row[0])
        )
    
    # Log progress
    if offset % 1000 == 0:
        logger.info(f"Processed {offset}/{total}...")

await db.commit()
```

## 📋 Migration Checklist

Before committing a migration:

- [ ] Version number is sequential (001, 002, 003...)
- [ ] Migration name is descriptive
- [ ] Uses `IF NOT EXISTS` for idempotency
- [ ] Both `up()` and `down()` methods implemented
- [ ] Changes are committed with `await db.commit()`
- [ ] Includes logging statements
- [ ] Tested locally (both up and down)
- [ ] Registered in `__init__.py`
- [ ] Documentation updated if needed

## 🔍 Checking Migration Status

### View All Migrations

```python
import asyncio
from database import get_database, get_migration_status

async def check():
    db = get_database()
    await db.connect()
    
    status = await get_migration_status(db)
    for m in status:
        print(f"{'✓' if m['applied'] else '✗'} {m['version']}: {m['name']}")
    
    await db.disconnect()

asyncio.run(check())
```

### Check Database Directly

```bash
sqlite3 data/contacts.db "SELECT version, name, applied_at FROM _migrations;"
```

## 🐛 Troubleshooting

### Migration Failed Partway Through

```bash
# 1. Check the error in logs
# 2. Fix the migration code
# 3. Remove the migration record
sqlite3 data/contacts.db "DELETE FROM _migrations WHERE version = '002';"
# 4. Restart the application (migration will retry)
```

### Table Already Exists Error

- Add `IF NOT EXISTS` to CREATE TABLE statements
- Check if migration was partially applied

### Migration Marked as Applied But Incomplete

```sql
-- Remove the migration record
DELETE FROM _migrations WHERE version = '002';
-- Then restart the app to rerun it
```

### Need to Reset Everything (Dev Only!)

```bash
python manage_migrations.py reset
```

## ⚠️ Important Rules

### DO:
✅ Use 3-digit zero-padded versions (001, 002, 003)  
✅ Keep migrations small and focused  
✅ Use `IF NOT EXISTS` everywhere  
✅ Test both `up()` and `down()` methods  
✅ Log progress for long operations  
✅ Process data in batches  
✅ Commit at the end of migration  

### DON'T:
❌ Modify migrations after they're applied  
❌ Delete migration files  
❌ Reuse version numbers  
❌ Mix unrelated changes  
❌ Forget to implement `down()`  
❌ Hardcode configuration values  

## 📚 Key Files

```
backend/src/database/
├── migrations/
│   ├── __init__.py                    # Register new migrations here
│   ├── migration_001_initial_schema.py
│   ├── migration_002_*.py             # Your new migrations
│   └── README.md                      # Full documentation
└── migration_runner.py                # Backward compatibility
```

## 🔄 Migration Lifecycle

```
1. Create migration file (migration_XXX_name.py)
2. Implement up() and down() methods
3. Register in __init__.py
4. Test locally
5. Commit to version control
6. Deploy (migrations run automatically on startup)
```

## 📊 Migration States

- **Pending**: Registered but not applied
- **Applied**: Successfully executed and tracked in `_migrations` table
- **Failed**: Attempted but errored (not marked as applied, will retry)

## 🎓 Examples

See `src/database/migrations/migration_002_example_template.py.example` for:
- Complete working examples
- Best practices
- Common patterns
- Error handling
- Data migration examples

## 🚨 Emergency Procedures

### Production Migration Failed

1. **Don't panic** - failed migrations aren't marked as applied
2. Check logs for the exact error
3. Hotfix the migration file if possible
4. Or rollback and fix properly
5. Redeploy with fixed migration

### Need to Rollback in Production

```bash
# This rolls back the LAST applied migration
python manage_migrations.py rollback
```

## 💡 Pro Tips

1. **Test migrations on a copy of production data** before deploying
2. **Use transactions** - migrations are wrapped in transactions where possible
3. **Log everything** - helps debug issues in production
4. **Keep migrations reversible** - always implement `down()`
5. **Version control** - migrations are code, commit them with your changes
6. **Sequential versions** - easier to track than timestamps
7. **Descriptive names** - future you will thank you

## 📞 Need Help?

- Check `migrations/README.md` for detailed documentation
- Look at `migration_002_example_template.py.example` for examples
- Review existing migrations for patterns
- Check the logs - migrations log extensively

---

**Quick Start**: Create file → Write code → Register → Test → Deploy 🚀
"""
Database Package
Handles SQLite database connections, migrations, and schema management

This package provides:
- Async database connection management
- Migration system with version tracking
- Schema verification and validation
- Database statistics and utilities

Migration System:
- Each migration is a separate file in database/migrations/
- Migrations are tracked in the _migrations table
- Migrations run only once, regardless of restart count
- Supports rollback capabilities

Usage:
    from database import get_database, run_migrations

    db = get_database()
    await db.connect()
    await run_migrations(db)
"""

from .connection import DatabaseConnection, get_database, init_database, close_database
from .migration_runner import (
    run_migrations,
    verify_schema,
    create_tables,
    get_schema_version,
    get_database_stats,
    drop_all_tables,
    reset_database,
    get_migration_status,
    Migration,
    MigrationManager,
    get_migration_manager,
    SCHEMA_VERSION,
)

__all__ = [
    # Connection management
    "DatabaseConnection",
    "get_database",
    "init_database",
    "close_database",
    # Migration functions
    "run_migrations",
    "verify_schema",
    "create_tables",
    "get_schema_version",
    "get_database_stats",
    "drop_all_tables",
    "reset_database",
    "get_migration_status",
    # Migration classes
    "Migration",
    "MigrationManager",
    "get_migration_manager",
    # Constants
    "SCHEMA_VERSION",
]

__version__ = "1.0.0"

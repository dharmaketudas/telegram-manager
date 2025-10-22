"""
Database Migrations - Compatibility Wrapper

This module provides backward compatibility with the old migration system
while using the new structured migration system under the hood.

The new migration system:
- Tracks applied migrations in a _migrations table
- Runs migrations only once
- Supports individual migration files with version control
- Provides rollback capabilities

Migration files are located in: database/migrations/
Each migration is a separate file following the pattern: migration_XXX_description.py
"""

import logging
from typing import Dict, List
from .connection import DatabaseConnection
from .migrations import (
    run_migrations as _run_migrations,
    verify_schema as _verify_schema,
    get_migration_status as _get_migration_status,
    Migration,
    MigrationManager,
    get_migration_manager,
)

logger = logging.getLogger(__name__)

# Schema version constant for backward compatibility
SCHEMA_VERSION = 1


async def create_tables(db: DatabaseConnection) -> bool:
    """
    Create all database tables with proper schema

    DEPRECATED: This function now calls the new migration system.
    Migrations are tracked and only run once.

    Args:
        db: DatabaseConnection instance

    Returns:
        True if successful, False otherwise
    """
    logger.info("create_tables() called - delegating to migration system")
    return await _run_migrations(db)


async def get_schema_version(db: DatabaseConnection) -> int:
    """
    Get current schema version from database

    Args:
        db: DatabaseConnection instance

    Returns:
        Current schema version, 0 if not set
    """
    try:
        # Check if we have any applied migrations
        manager = get_migration_manager(db)
        await manager.init_migrations_table()

        applied = await manager.get_applied_migrations()

        if not applied:
            return 0

        # Return the highest migration version as an integer
        versions = [int(v) for v in applied.keys()]
        return max(versions) if versions else 0
    except Exception as e:
        logger.warning(f"Could not get schema version: {e}")
        return 0


async def get_database_stats(db: DatabaseConnection) -> dict:
    """
    Get statistics about database contents

    Args:
        db: DatabaseConnection instance

    Returns:
        Dictionary with table row counts
    """
    stats = {}

    tables = ["contacts", "groups", "tags", "messages", "sync_log"]

    for table in tables:
        try:
            count = await db.get_table_count(table)
            stats[table] = count
        except Exception as e:
            logger.error(f"Error getting count for {table}: {e}")
            stats[table] = -1

    return stats


async def drop_all_tables(db: DatabaseConnection):
    """
    Drop all tables from database
    WARNING: This will delete all data!

    Args:
        db: DatabaseConnection instance
    """
    logger.warning("Dropping all database tables...")

    tables = [
        "contact_tags",
        "contact_groups",
        "messages",
        "contacts",
        "groups",
        "tags",
        "session_config",
        "sync_log",
        "_migrations",  # Also drop the migrations tracking table
    ]

    for table in tables:
        await db.execute(f"DROP TABLE IF EXISTS {table}")

    await db.commit()
    logger.warning("All tables dropped")


async def reset_database(db: DatabaseConnection) -> bool:
    """
    Reset database by dropping and recreating all tables
    WARNING: This will delete all data!

    Args:
        db: DatabaseConnection instance

    Returns:
        True if successful, False otherwise
    """
    logger.warning("Resetting database...")
    await drop_all_tables(db)
    return await _run_migrations(db)


# Re-export functions from migrations package for backward compatibility
run_migrations = _run_migrations
verify_schema = _verify_schema
get_migration_status = _get_migration_status

# Export all functions for backward compatibility
__all__ = [
    "run_migrations",
    "verify_schema",
    "create_tables",
    "get_schema_version",
    "get_database_stats",
    "drop_all_tables",
    "reset_database",
    "get_migration_status",
    "Migration",
    "MigrationManager",
    "get_migration_manager",
    "SCHEMA_VERSION",
]

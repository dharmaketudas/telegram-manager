"""
Database Migration System
Tracks and executes database migrations with proper versioning
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class Migration:
    """Represents a single database migration"""

    def __init__(self, version: str, name: str, description: str = ""):
        self.version = version
        self.name = name
        self.description = description
        self.applied_at: Optional[datetime] = None

    async def up(self, db: DatabaseConnection):
        """Apply the migration"""
        raise NotImplementedError("Subclasses must implement up()")

    async def down(self, db: DatabaseConnection):
        """Rollback the migration (optional)"""
        raise NotImplementedError("Subclasses must implement down()")

    def __repr__(self):
        return f"Migration({self.version}: {self.name})"


class MigrationManager:
    """Manages database migrations with tracking and execution"""

    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.migrations: List[Migration] = []

    async def init_migrations_table(self):
        """Create the migrations tracking table if it doesn't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS _migrations (
            version TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checksum TEXT
        );
        """
        await self.db.execute(create_table_sql)
        await self.db.commit()
        logger.info("Migrations tracking table initialized")

    async def get_applied_migrations(self) -> Dict[str, datetime]:
        """Get list of already applied migrations"""
        try:
            rows = await self.db.fetch_all(
                "SELECT version, applied_at FROM _migrations ORDER BY version"
            )
            return {row[0]: row[1] for row in rows}
        except Exception as e:
            logger.warning(f"Could not fetch applied migrations: {e}")
            return {}

    async def mark_migration_applied(self, migration: Migration):
        """Mark a migration as applied"""
        await self.db.execute(
            """
            INSERT INTO _migrations (version, name, description, applied_at)
            VALUES (?, ?, ?, ?)
            """,
            (migration.version, migration.name, migration.description, datetime.now()),
        )
        await self.db.commit()
        logger.info(
            f"Marked migration as applied: {migration.version} - {migration.name}"
        )

    async def is_migration_applied(self, version: str) -> bool:
        """Check if a specific migration has been applied"""
        result = await self.db.fetch_one(
            "SELECT version FROM _migrations WHERE version = ?", (version,)
        )
        return result is not None

    def register_migration(self, migration: Migration):
        """Register a migration to be tracked"""
        self.migrations.append(migration)
        # Keep migrations sorted by version
        self.migrations.sort(key=lambda m: m.version)

    async def run_pending_migrations(self) -> bool:
        """Run all pending migrations that haven't been applied yet"""
        try:
            # Ensure migrations table exists
            await self.init_migrations_table()

            # Get applied migrations
            applied = await self.get_applied_migrations()

            # Find pending migrations
            pending = [m for m in self.migrations if m.version not in applied]

            if not pending:
                logger.info("No pending migrations to run")
                return True

            logger.info(f"Found {len(pending)} pending migration(s) to run")

            # Run each pending migration
            for migration in pending:
                logger.info(
                    f"Running migration: {migration.version} - {migration.name}"
                )

                try:
                    # Execute the migration
                    await migration.up(self.db)

                    # Mark as applied
                    await self.mark_migration_applied(migration)

                    logger.info(
                        f"✓ Successfully applied migration: {migration.version}"
                    )

                except Exception as e:
                    logger.error(
                        f"✗ Failed to apply migration {migration.version}: {e}"
                    )
                    # Don't mark as applied, will retry next time
                    raise

            logger.info(f"All migrations completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            return False

    async def get_migration_status(self) -> List[Dict]:
        """Get status of all registered migrations"""
        applied = await self.get_applied_migrations()

        status = []
        for migration in self.migrations:
            status.append(
                {
                    "version": migration.version,
                    "name": migration.name,
                    "description": migration.description,
                    "applied": migration.version in applied,
                    "applied_at": applied.get(migration.version),
                }
            )

        return status

    async def rollback_last_migration(self) -> bool:
        """Rollback the last applied migration"""
        try:
            # Get last applied migration
            row = await self.db.fetch_one(
                "SELECT version FROM _migrations ORDER BY applied_at DESC LIMIT 1"
            )

            if not row:
                logger.warning("No migrations to rollback")
                return False

            version = row[0]

            # Find the migration
            migration = next((m for m in self.migrations if m.version == version), None)

            if not migration:
                logger.error(f"Migration {version} not found in registered migrations")
                return False

            logger.info(f"Rolling back migration: {version} - {migration.name}")

            # Execute rollback
            await migration.down(self.db)

            # Remove from tracking table
            await self.db.execute(
                "DELETE FROM _migrations WHERE version = ?", (version,)
            )
            await self.db.commit()

            logger.info(f"✓ Successfully rolled back migration: {version}")
            return True

        except Exception as e:
            logger.error(f"Error rolling back migration: {e}")
            return False


# Global migration manager instance
_migration_manager: Optional[MigrationManager] = None


def get_migration_manager(db: DatabaseConnection) -> MigrationManager:
    """Get or create the global migration manager"""
    global _migration_manager
    if _migration_manager is None or _migration_manager.db != db:
        _migration_manager = MigrationManager(db)
    return _migration_manager


def _register_all_migrations(manager: MigrationManager):
    """
    Register all migration files with the migration manager

    This function imports and registers all migration files.
    Add new migrations here when you create them.

    Args:
        manager: MigrationManager instance
    """
    # Import and register all migration files
    from . import migration_001_initial_schema

    # Register migrations
    manager.register_migration(migration_001_initial_schema.InitialSchemaMigration())

    # Add new migrations here as you create them:
    # from . import migration_002_your_migration
    # manager.register_migration(migration_002_your_migration.YourMigration())


async def run_migrations(db: DatabaseConnection) -> bool:
    """
    Main entry point for running migrations
    Discovers and runs all pending migrations

    Args:
        db: DatabaseConnection instance

    Returns:
        True if successful, False otherwise
    """
    logger.info("Starting migration process...")

    manager = get_migration_manager(db)

    # Register all migrations
    _register_all_migrations(manager)

    # Run pending migrations
    success = await manager.run_pending_migrations()

    if success:
        logger.info("Migration process completed successfully")
    else:
        logger.error("Migration process failed")

    return success


async def get_migration_status(db: DatabaseConnection) -> List[Dict]:
    """Get status of all migrations"""
    manager = get_migration_manager(db)

    # Register all migrations so we can check their status
    _register_all_migrations(manager)

    return await manager.get_migration_status()


async def verify_schema(db: DatabaseConnection) -> bool:
    """
    Verify that all required tables exist

    Args:
        db: DatabaseConnection instance

    Returns:
        True if all tables exist, False otherwise
    """
    required_tables = [
        "contacts",
        "groups",
        "tags",
        "contact_tags",
        "contact_groups",
        "messages",
        "session_config",
        "sync_log",
    ]

    for table in required_tables:
        if not await db.table_exists(table):
            logger.error(f"Required table missing: {table}")
            return False

    logger.info("Database schema verification passed")
    return True


__all__ = [
    "Migration",
    "MigrationManager",
    "get_migration_manager",
    "run_migrations",
    "get_migration_status",
    "verify_schema",
]

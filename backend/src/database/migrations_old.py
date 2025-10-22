"""
Database Migrations
Contains SQL schema definitions and migration functions
"""

import logging
from typing import List
from .connection import DatabaseConnection

logger = logging.getLogger(__name__)


# SQL Schema Definitions
SCHEMA_VERSION = 1

CREATE_CONTACTS_TABLE = """
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    display_name TEXT NOT NULL,
    phone TEXT,
    profile_photo_path TEXT,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_GROUPS_TABLE = """
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    member_count INTEGER DEFAULT 0,
    profile_photo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_CONTACT_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS contact_tags (
    contact_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contact_id, tag_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
"""

CREATE_CONTACT_GROUPS_TABLE = """
CREATE TABLE IF NOT EXISTS contact_groups (
    contact_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contact_id, group_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);
"""

CREATE_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_message_id INTEGER,
    contact_id INTEGER NOT NULL,
    is_outgoing BOOLEAN NOT NULL,
    content TEXT,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);
"""

CREATE_SESSION_CONFIG_TABLE = """
CREATE TABLE IF NOT EXISTS session_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_SYNC_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_type TEXT NOT NULL,
    status TEXT NOT NULL,
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
"""

# Index Definitions for Performance
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_contacts_telegram_id ON contacts(telegram_id);",
    "CREATE INDEX IF NOT EXISTS idx_contacts_username ON contacts(username);",
    "CREATE INDEX IF NOT EXISTS idx_contacts_display_name ON contacts(display_name);",
    "CREATE INDEX IF NOT EXISTS idx_groups_telegram_id ON groups(telegram_id);",
    "CREATE INDEX IF NOT EXISTS idx_groups_name ON groups(name);",
    "CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON messages(contact_id);",
    "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);",
    "CREATE INDEX IF NOT EXISTS idx_messages_is_outgoing ON messages(is_outgoing);",
    "CREATE INDEX IF NOT EXISTS idx_contact_tags_tag_id ON contact_tags(tag_id);",
    "CREATE INDEX IF NOT EXISTS idx_contact_tags_contact_id ON contact_tags(contact_id);",
    "CREATE INDEX IF NOT EXISTS idx_contact_groups_group_id ON contact_groups(group_id);",
    "CREATE INDEX IF NOT EXISTS idx_contact_groups_contact_id ON contact_groups(contact_id);",
    "CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);",
    "CREATE INDEX IF NOT EXISTS idx_sync_log_sync_type ON sync_log(sync_type);",
    "CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log(status);",
]

# Trigger for updating updated_at timestamp
CREATE_CONTACTS_UPDATE_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS update_contacts_timestamp
AFTER UPDATE ON contacts
FOR EACH ROW
BEGIN
    UPDATE contacts SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
"""

CREATE_GROUPS_UPDATE_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS update_groups_timestamp
AFTER UPDATE ON groups
FOR EACH ROW
BEGIN
    UPDATE groups SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
"""

CREATE_SESSION_CONFIG_UPDATE_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS update_session_config_timestamp
AFTER UPDATE ON session_config
FOR EACH ROW
BEGIN
    UPDATE session_config SET updated_at = CURRENT_TIMESTAMP
    WHERE key = NEW.key;
END;
"""


async def create_tables(db: DatabaseConnection) -> bool:
    """
    Create all database tables with proper schema

    Args:
        db: DatabaseConnection instance

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating database tables...")

        # Create tables in order (respecting foreign key dependencies)
        tables = [
            ("contacts", CREATE_CONTACTS_TABLE),
            ("groups", CREATE_GROUPS_TABLE),
            ("tags", CREATE_TAGS_TABLE),
            ("contact_tags", CREATE_CONTACT_TAGS_TABLE),
            ("contact_groups", CREATE_CONTACT_GROUPS_TABLE),
            ("messages", CREATE_MESSAGES_TABLE),
            ("session_config", CREATE_SESSION_CONFIG_TABLE),
            ("sync_log", CREATE_SYNC_LOG_TABLE),
        ]

        for table_name, create_sql in tables:
            await db.execute(create_sql)
            logger.info(f"Created table: {table_name}")

        # Create indexes
        logger.info("Creating indexes...")
        for index_sql in CREATE_INDEXES:
            await db.execute(index_sql)

        # Create triggers
        logger.info("Creating triggers...")
        await db.execute(CREATE_CONTACTS_UPDATE_TRIGGER)
        await db.execute(CREATE_GROUPS_UPDATE_TRIGGER)
        await db.execute(CREATE_SESSION_CONFIG_UPDATE_TRIGGER)

        # Commit all changes
        await db.commit()

        logger.info("Database schema created successfully")
        return True

    except Exception as e:
        logger.error(f"Error creating database schema: {e}")
        await db.rollback()
        return False


async def get_schema_version(db: DatabaseConnection) -> int:
    """
    Get current schema version from database

    Args:
        db: DatabaseConnection instance

    Returns:
        Current schema version, 0 if not set
    """
    try:
        result = await db.fetch_one(
            "SELECT value FROM session_config WHERE key = 'schema_version'"
        )
        if result:
            return int(result[0])
        return 0
    except Exception:
        return 0


async def set_schema_version(db: DatabaseConnection, version: int):
    """
    Set schema version in database

    Args:
        db: DatabaseConnection instance
        version: Schema version number
    """
    await db.execute(
        """
        INSERT OR REPLACE INTO session_config (key, value)
        VALUES ('schema_version', ?)
        """,
        (str(version),),
    )
    await db.commit()


async def run_migrations(db: DatabaseConnection) -> bool:
    """
    Run database migrations to bring schema up to date

    Args:
        db: DatabaseConnection instance

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Running database migrations...")

        # Create base schema
        success = await create_tables(db)
        if not success:
            return False

        # Get current version
        current_version = await get_schema_version(db)
        logger.info(f"Current schema version: {current_version}")

        # Run version-specific migrations
        if current_version < 1:
            logger.info("Running migration to version 1...")
            # Version 1 is the initial schema (already created above)
            await set_schema_version(db, 1)

        # Future migrations would go here
        # if current_version < 2:
        #     logger.info("Running migration to version 2...")
        #     # Add new columns, tables, etc.
        #     await set_schema_version(db, 2)

        logger.info(f"Migrations complete. Schema version: {SCHEMA_VERSION}")
        return True

    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False


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
    return await run_migrations(db)


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

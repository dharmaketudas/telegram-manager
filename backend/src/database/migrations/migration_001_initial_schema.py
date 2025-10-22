"""
Migration 001: Initial Schema
Creates the base database schema with all tables, indexes, and triggers
"""

import logging
from . import Migration
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class InitialSchemaMigration(Migration):
    """Initial database schema migration"""

    def __init__(self):
        super().__init__(
            version="001",
            name="initial_schema",
            description="Create base database schema with contacts, groups, tags, messages, and configuration tables",
        )

    async def up(self, db: DatabaseConnection):
        """Create all initial tables, indexes, and triggers"""
        logger.info("Creating initial database schema...")

        # Create contacts table
        await db.execute("""
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
        """)
        logger.info("Created table: contacts")

        # Create groups table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                member_count INTEGER DEFAULT 0,
                profile_photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logger.info("Created table: groups")

        # Create tags table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logger.info("Created table: tags")

        # Create contact_tags junction table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS contact_tags (
                contact_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (contact_id, tag_id),
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            );
        """)
        logger.info("Created table: contact_tags")

        # Create contact_groups junction table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS contact_groups (
                contact_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (contact_id, group_id),
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
            );
        """)
        logger.info("Created table: contact_groups")

        # Create messages table
        await db.execute("""
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
        """)
        logger.info("Created table: messages")

        # Create session_config table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS session_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logger.info("Created table: session_config")

        # Create sync_log table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_type TEXT NOT NULL,
                status TEXT NOT NULL,
                records_processed INTEGER DEFAULT 0,
                error_message TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );
        """)
        logger.info("Created table: sync_log")

        # Create indexes for performance
        logger.info("Creating indexes...")

        indexes = [
            ("idx_contacts_telegram_id", "contacts", "telegram_id"),
            ("idx_contacts_username", "contacts", "username"),
            ("idx_contacts_display_name", "contacts", "display_name"),
            ("idx_groups_telegram_id", "groups", "telegram_id"),
            ("idx_groups_name", "groups", "name"),
            ("idx_messages_contact_id", "messages", "contact_id"),
            ("idx_messages_timestamp", "messages", "timestamp DESC"),
            ("idx_messages_is_outgoing", "messages", "is_outgoing"),
            ("idx_contact_tags_tag_id", "contact_tags", "tag_id"),
            ("idx_contact_tags_contact_id", "contact_tags", "contact_id"),
            ("idx_contact_groups_group_id", "contact_groups", "group_id"),
            ("idx_contact_groups_contact_id", "contact_groups", "contact_id"),
            ("idx_tags_name", "tags", "name"),
            ("idx_sync_log_sync_type", "sync_log", "sync_type"),
            ("idx_sync_log_status", "sync_log", "status"),
        ]

        for index_name, table_name, column_spec in indexes:
            await db.execute(
                f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_spec});"
            )

        logger.info(f"Created {len(indexes)} indexes")

        # Create triggers for automatic timestamp updates
        logger.info("Creating triggers...")

        # Contacts update trigger
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS update_contacts_timestamp
            AFTER UPDATE ON contacts
            FOR EACH ROW
            BEGIN
                UPDATE contacts SET updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.id;
            END;
        """)

        # Groups update trigger
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS update_groups_timestamp
            AFTER UPDATE ON groups
            FOR EACH ROW
            BEGIN
                UPDATE groups SET updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.id;
            END;
        """)

        # Session config update trigger
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS update_session_config_timestamp
            AFTER UPDATE ON session_config
            FOR EACH ROW
            BEGIN
                UPDATE session_config SET updated_at = CURRENT_TIMESTAMP
                WHERE key = NEW.key;
            END;
        """)

        logger.info("Created 3 triggers")

        # Commit all changes
        await db.commit()

        logger.info("✓ Initial schema created successfully")

    async def down(self, db: DatabaseConnection):
        """Drop all tables created by this migration"""
        logger.warning("Rolling back initial schema (dropping all tables)...")

        # Drop tables in reverse order of dependencies
        tables = [
            "contact_tags",
            "contact_groups",
            "messages",
            "sync_log",
            "session_config",
            "tags",
            "groups",
            "contacts",
        ]

        for table in tables:
            await db.execute(f"DROP TABLE IF EXISTS {table}")
            logger.info(f"Dropped table: {table}")

        await db.commit()

        logger.warning("✓ Initial schema rolled back successfully")

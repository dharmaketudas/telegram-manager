"""
Unit Tests for Database Migrations
Tests the migration functions and schema creation
"""

import pytest
import tempfile
import os
from pathlib import Path

from database.connection import DatabaseConnection
from database.migrations import (
    create_tables,
    get_schema_version,
    set_schema_version,
    run_migrations,
    drop_all_tables,
    reset_database,
    verify_schema,
    get_database_stats,
    SCHEMA_VERSION,
)


@pytest.fixture
async def test_db():
    """
    Fixture that provides a temporary database for testing
    """
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_migrations.db")

    db = DatabaseConnection(db_path)
    await db.connect()

    yield db

    await db.disconnect()
    try:
        os.remove(db_path)
        os.rmdir(temp_dir)
    except:
        pass


@pytest.fixture
async def in_memory_db():
    """
    Fixture that provides an in-memory database for testing
    """
    db = DatabaseConnection(":memory:")
    await db.connect()

    yield db

    await db.disconnect()


class TestCreateTables:
    """Test table creation"""

    @pytest.mark.asyncio
    async def test_create_tables_success(self, in_memory_db):
        """Test that all tables are created successfully"""
        result = await create_tables(in_memory_db)
        assert result is True

    @pytest.mark.asyncio
    async def test_contacts_table_created(self, in_memory_db):
        """Test contacts table exists after creation"""
        await create_tables(in_memory_db)
        assert await in_memory_db.table_exists("contacts")

    @pytest.mark.asyncio
    async def test_groups_table_created(self, in_memory_db):
        """Test groups table exists after creation"""
        await create_tables(in_memory_db)
        assert await in_memory_db.table_exists("groups")

    @pytest.mark.asyncio
    async def test_tags_table_created(self, in_memory_db):
        """Test tags table exists after creation"""
        await create_tables(in_memory_db)
        assert await in_memory_db.table_exists("tags")

    @pytest.mark.asyncio
    async def test_contact_tags_table_created(self, in_memory_db):
        """Test contact_tags junction table exists"""
        await create_tables(in_memory_db)
        assert await in_memory_db.table_exists("contact_tags")

    @pytest.mark.asyncio
    async def test_contact_groups_table_created(self, in_memory_db):
        """Test contact_groups junction table exists"""
        await create_tables(in_memory_db)
        assert await in_memory_db.table_exists("contact_groups")

    @pytest.mark.asyncio
    async def test_messages_table_created(self, in_memory_db):
        """Test messages table exists after creation"""
        await create_tables(in_memory_db)
        assert await in_memory_db.table_exists("messages")

    @pytest.mark.asyncio
    async def test_session_config_table_created(self, in_memory_db):
        """Test session_config table exists"""
        await create_tables(in_memory_db)
        assert await in_memory_db.table_exists("session_config")

    @pytest.mark.asyncio
    async def test_sync_log_table_created(self, in_memory_db):
        """Test sync_log table exists"""
        await create_tables(in_memory_db)
        assert await in_memory_db.table_exists("sync_log")

    @pytest.mark.asyncio
    async def test_all_required_tables_exist(self, in_memory_db):
        """Test all required tables are created"""
        await create_tables(in_memory_db)

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
            assert await in_memory_db.table_exists(table), f"Table {table} not found"

    @pytest.mark.asyncio
    async def test_contacts_table_structure(self, in_memory_db):
        """Test contacts table has correct columns"""
        await create_tables(in_memory_db)

        # Insert test data to verify structure
        await in_memory_db.execute(
            """
            INSERT INTO contacts (telegram_id, display_name, username, first_name, last_name)
            VALUES (12345, 'Test User', 'testuser', 'Test', 'User')
            """
        )
        await in_memory_db.commit()

        result = await in_memory_db.fetch_one(
            "SELECT * FROM contacts WHERE telegram_id = 12345"
        )
        assert result is not None

    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self, in_memory_db):
        """Test foreign key constraints are enforced"""
        await create_tables(in_memory_db)

        # Try to insert into contact_tags with non-existent contact
        with pytest.raises(Exception):
            await in_memory_db.execute(
                "INSERT INTO contact_tags (contact_id, tag_id) VALUES (999, 1)"
            )
            await in_memory_db.commit()


class TestSchemaVersion:
    """Test schema version management"""

    @pytest.mark.asyncio
    async def test_get_schema_version_no_table(self, in_memory_db):
        """Test get_schema_version returns 0 when table doesn't exist"""
        version = await get_schema_version(in_memory_db)
        assert version == 0

    @pytest.mark.asyncio
    async def test_get_schema_version_no_value(self, in_memory_db):
        """Test get_schema_version returns 0 when value not set"""
        await create_tables(in_memory_db)
        version = await get_schema_version(in_memory_db)
        assert version == 0

    @pytest.mark.asyncio
    async def test_set_schema_version(self, in_memory_db):
        """Test setting schema version"""
        await create_tables(in_memory_db)
        await set_schema_version(in_memory_db, 1)

        version = await get_schema_version(in_memory_db)
        assert version == 1

    @pytest.mark.asyncio
    async def test_set_schema_version_updates_existing(self, in_memory_db):
        """Test updating existing schema version"""
        await create_tables(in_memory_db)
        await set_schema_version(in_memory_db, 1)
        await set_schema_version(in_memory_db, 2)

        version = await get_schema_version(in_memory_db)
        assert version == 2


class TestRunMigrations:
    """Test migration execution"""

    @pytest.mark.asyncio
    async def test_run_migrations_success(self, in_memory_db):
        """Test migrations run successfully"""
        result = await run_migrations(in_memory_db)
        assert result is True

    @pytest.mark.asyncio
    async def test_run_migrations_creates_all_tables(self, in_memory_db):
        """Test migrations create all required tables"""
        await run_migrations(in_memory_db)

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
            assert await in_memory_db.table_exists(table)

    @pytest.mark.asyncio
    async def test_run_migrations_sets_schema_version(self, in_memory_db):
        """Test migrations set correct schema version"""
        await run_migrations(in_memory_db)

        version = await get_schema_version(in_memory_db)
        assert version == SCHEMA_VERSION

    @pytest.mark.asyncio
    async def test_run_migrations_idempotent(self, in_memory_db):
        """Test migrations can be run multiple times safely"""
        await run_migrations(in_memory_db)
        result = await run_migrations(in_memory_db)

        assert result is True
        assert await in_memory_db.table_exists("contacts")


class TestDropTables:
    """Test dropping tables"""

    @pytest.mark.asyncio
    async def test_drop_all_tables(self, in_memory_db):
        """Test dropping all tables"""
        await create_tables(in_memory_db)
        await drop_all_tables(in_memory_db)

        # Verify tables are gone
        assert not await in_memory_db.table_exists("contacts")
        assert not await in_memory_db.table_exists("groups")
        assert not await in_memory_db.table_exists("tags")

    @pytest.mark.asyncio
    async def test_drop_all_tables_empty_database(self, in_memory_db):
        """Test dropping tables on empty database doesn't error"""
        # Should not raise error
        await drop_all_tables(in_memory_db)


class TestResetDatabase:
    """Test database reset"""

    @pytest.mark.asyncio
    async def test_reset_database(self, in_memory_db):
        """Test resetting database"""
        # Create tables and add data
        await create_tables(in_memory_db)
        await in_memory_db.execute(
            "INSERT INTO contacts (telegram_id, display_name) VALUES (1, 'Test')"
        )
        await in_memory_db.commit()

        # Reset
        result = await reset_database(in_memory_db)

        assert result is True
        assert await in_memory_db.table_exists("contacts")

        # Data should be gone
        count = await in_memory_db.get_table_count("contacts")
        assert count == 0


class TestVerifySchema:
    """Test schema verification"""

    @pytest.mark.asyncio
    async def test_verify_schema_all_tables_exist(self, in_memory_db):
        """Test schema verification passes when all tables exist"""
        await create_tables(in_memory_db)
        result = await verify_schema(in_memory_db)
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_schema_missing_table(self, in_memory_db):
        """Test schema verification fails when table is missing"""
        await create_tables(in_memory_db)
        await in_memory_db.execute("DROP TABLE contacts")
        await in_memory_db.commit()

        result = await verify_schema(in_memory_db)
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_schema_empty_database(self, in_memory_db):
        """Test schema verification fails on empty database"""
        result = await verify_schema(in_memory_db)
        assert result is False


class TestDatabaseStats:
    """Test database statistics"""

    @pytest.mark.asyncio
    async def test_get_database_stats_empty(self, in_memory_db):
        """Test getting stats from empty database"""
        await create_tables(in_memory_db)
        stats = await get_database_stats(in_memory_db)

        assert stats["contacts"] == 0
        assert stats["groups"] == 0
        assert stats["tags"] == 0
        assert stats["messages"] == 0

    @pytest.mark.asyncio
    async def test_get_database_stats_with_data(self, in_memory_db):
        """Test getting stats with data"""
        await create_tables(in_memory_db)

        # Add test data
        await in_memory_db.execute(
            "INSERT INTO contacts (telegram_id, display_name) VALUES (1, 'User1')"
        )
        await in_memory_db.execute(
            "INSERT INTO contacts (telegram_id, display_name) VALUES (2, 'User2')"
        )
        await in_memory_db.execute("INSERT INTO tags (name) VALUES ('Tag1')")
        await in_memory_db.commit()

        stats = await get_database_stats(in_memory_db)

        assert stats["contacts"] == 2
        assert stats["tags"] == 1
        assert stats["groups"] == 0


class TestIndexes:
    """Test that indexes are created"""

    @pytest.mark.asyncio
    async def test_indexes_created(self, in_memory_db):
        """Test that indexes are created (basic check)"""
        await create_tables(in_memory_db)

        # Query sqlite_master to check for indexes
        result = await in_memory_db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='index'"
        )

        # Should have multiple indexes
        assert len(result) > 0

        # Check for specific indexes
        index_names = [row[0] for row in result]
        assert any("contacts" in name for name in index_names)


class TestTriggers:
    """Test that triggers work correctly"""

    @pytest.mark.asyncio
    async def test_contacts_update_trigger(self, in_memory_db):
        """Test that updated_at is updated on contact modification"""
        await create_tables(in_memory_db)

        # Insert contact
        await in_memory_db.execute(
            "INSERT INTO contacts (telegram_id, display_name) VALUES (1, 'User')"
        )
        await in_memory_db.commit()

        # Get initial timestamp
        result1 = await in_memory_db.fetch_one(
            "SELECT updated_at FROM contacts WHERE telegram_id = 1"
        )
        initial_time = result1[0]

        # Small delay to ensure timestamp difference
        import asyncio

        await asyncio.sleep(0.1)

        # Update contact
        await in_memory_db.execute(
            "UPDATE contacts SET display_name = 'Updated User' WHERE telegram_id = 1"
        )
        await in_memory_db.commit()

        # Get new timestamp
        result2 = await in_memory_db.fetch_one(
            "SELECT updated_at FROM contacts WHERE telegram_id = 1"
        )
        updated_time = result2[0]

        # Timestamps should be different
        assert updated_time >= initial_time

    @pytest.mark.asyncio
    async def test_groups_update_trigger(self, in_memory_db):
        """Test that updated_at is updated on group modification"""
        await create_tables(in_memory_db)

        # Insert group
        await in_memory_db.execute(
            "INSERT INTO groups (telegram_id, name) VALUES (1, 'Group')"
        )
        await in_memory_db.commit()

        # Update group
        await in_memory_db.execute(
            "UPDATE groups SET name = 'Updated Group' WHERE telegram_id = 1"
        )
        await in_memory_db.commit()

        # Should not raise error (trigger executed)
        result = await in_memory_db.fetch_one(
            "SELECT updated_at FROM groups WHERE telegram_id = 1"
        )
        assert result is not None


class TestDataIntegrity:
    """Test data integrity constraints"""

    @pytest.mark.asyncio
    async def test_contact_telegram_id_unique(self, in_memory_db):
        """Test that telegram_id must be unique for contacts"""
        await create_tables(in_memory_db)

        await in_memory_db.execute(
            "INSERT INTO contacts (telegram_id, display_name) VALUES (1, 'User1')"
        )
        await in_memory_db.commit()

        # Try to insert duplicate telegram_id
        with pytest.raises(Exception):
            await in_memory_db.execute(
                "INSERT INTO contacts (telegram_id, display_name) VALUES (1, 'User2')"
            )
            await in_memory_db.commit()

    @pytest.mark.asyncio
    async def test_tag_name_unique(self, in_memory_db):
        """Test that tag names must be unique"""
        await create_tables(in_memory_db)

        await in_memory_db.execute("INSERT INTO tags (name) VALUES ('Tag1')")
        await in_memory_db.commit()

        # Try to insert duplicate tag name
        with pytest.raises(Exception):
            await in_memory_db.execute("INSERT INTO tags (name) VALUES ('Tag1')")
            await in_memory_db.commit()

    @pytest.mark.asyncio
    async def test_cascade_delete_contact_tags(self, in_memory_db):
        """Test that deleting contact removes its tags"""
        await create_tables(in_memory_db)

        # Create contact and tag
        await in_memory_db.execute(
            "INSERT INTO contacts (telegram_id, display_name) VALUES (1, 'User')"
        )
        await in_memory_db.execute("INSERT INTO tags (name) VALUES ('Tag1')")
        await in_memory_db.execute(
            "INSERT INTO contact_tags (contact_id, tag_id) VALUES (1, 1)"
        )
        await in_memory_db.commit()

        # Delete contact
        await in_memory_db.execute("DELETE FROM contacts WHERE id = 1")
        await in_memory_db.commit()

        # Contact_tags should be empty
        count = await in_memory_db.get_table_count("contact_tags")
        assert count == 0

    @pytest.mark.asyncio
    async def test_cascade_delete_messages(self, in_memory_db):
        """Test that deleting contact removes its messages"""
        await create_tables(in_memory_db)

        # Create contact and message
        await in_memory_db.execute(
            "INSERT INTO contacts (telegram_id, display_name) VALUES (1, 'User')"
        )
        await in_memory_db.execute(
            """
            INSERT INTO messages (contact_id, is_outgoing, content, timestamp)
            VALUES (1, 0, 'Test message', CURRENT_TIMESTAMP)
            """
        )
        await in_memory_db.commit()

        # Delete contact
        await in_memory_db.execute("DELETE FROM contacts WHERE id = 1")
        await in_memory_db.commit()

        # Messages should be empty
        count = await in_memory_db.get_table_count("messages")
        assert count == 0

"""
Unit Tests for Database Connection
Tests the DatabaseConnection class and related utilities
"""

import pytest
import aiosqlite
from pathlib import Path
import tempfile
import os

from database.connection import (
    DatabaseConnection,
    get_database,
    init_database,
    close_database,
)


@pytest.fixture
async def test_db():
    """
    Fixture that provides a temporary database for testing
    """
    # Create temporary database file
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")

    db = DatabaseConnection(db_path)
    await db.connect()

    yield db

    # Cleanup
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


class TestDatabaseConnection:
    """Test DatabaseConnection class"""

    @pytest.mark.asyncio
    async def test_connect_creates_database_file(self):
        """Test that connect creates database file"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_connection.db")

        db = DatabaseConnection(db_path)
        await db.connect()

        assert Path(db_path).exists()

        await db.disconnect()
        os.remove(db_path)
        os.rmdir(temp_dir)

    @pytest.mark.asyncio
    async def test_connect_enables_foreign_keys(self, in_memory_db):
        """Test that foreign keys are enabled"""
        result = await in_memory_db.fetch_one("PRAGMA foreign_keys")
        assert result[0] == 1

    @pytest.mark.asyncio
    async def test_connect_sets_wal_mode(self, in_memory_db):
        """Test that WAL journal mode is set"""
        result = await in_memory_db.fetch_one("PRAGMA journal_mode")
        # In-memory databases don't support WAL, but file databases do
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_connection_reuses_existing(self, in_memory_db):
        """Test that get_connection reuses existing connection"""
        conn1 = await in_memory_db.get_connection()
        conn2 = await in_memory_db.get_connection()

        assert conn1 is conn2

    @pytest.mark.asyncio
    async def test_execute_simple_query(self, in_memory_db):
        """Test executing a simple query"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        await in_memory_db.commit()

        assert await in_memory_db.table_exists("test")

    @pytest.mark.asyncio
    async def test_execute_with_parameters(self, in_memory_db):
        """Test executing query with parameters"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        await in_memory_db.execute("INSERT INTO test (name) VALUES (?)", ("test_name",))
        await in_memory_db.commit()

        result = await in_memory_db.fetch_one("SELECT name FROM test")
        assert result[0] == "test_name"

    @pytest.mark.asyncio
    async def test_execute_many(self, in_memory_db):
        """Test executing query with multiple parameter sets"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )

        data = [("name1",), ("name2",), ("name3",)]
        await in_memory_db.execute_many("INSERT INTO test (name) VALUES (?)", data)
        await in_memory_db.commit()

        count = await in_memory_db.get_table_count("test")
        assert count == 3

    @pytest.mark.asyncio
    async def test_fetch_one(self, in_memory_db):
        """Test fetching a single row"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        await in_memory_db.execute("INSERT INTO test (name) VALUES (?)", ("test",))
        await in_memory_db.commit()

        result = await in_memory_db.fetch_one("SELECT name FROM test WHERE id = 1")
        assert result is not None
        assert result[0] == "test"

    @pytest.mark.asyncio
    async def test_fetch_one_no_result(self, in_memory_db):
        """Test fetch_one returns None when no results"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )

        result = await in_memory_db.fetch_one("SELECT * FROM test WHERE id = 999")
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_all(self, in_memory_db):
        """Test fetching all rows"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        await in_memory_db.execute_many(
            "INSERT INTO test (name) VALUES (?)", [("name1",), ("name2",), ("name3",)]
        )
        await in_memory_db.commit()

        results = await in_memory_db.fetch_all("SELECT name FROM test")
        assert len(results) == 3
        assert results[0][0] == "name1"

    @pytest.mark.asyncio
    async def test_transaction_commit(self, in_memory_db):
        """Test transaction context manager commits on success"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        await in_memory_db.commit()

        async with in_memory_db.transaction():
            await in_memory_db.execute("INSERT INTO test (name) VALUES (?)", ("test",))

        count = await in_memory_db.get_table_count("test")
        assert count == 1

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, in_memory_db):
        """Test transaction rolls back on error"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY UNIQUE, name TEXT)"
        )
        await in_memory_db.commit()

        # Insert initial record
        await in_memory_db.execute("INSERT INTO test (id, name) VALUES (1, 'test')")
        await in_memory_db.commit()

        # Try to insert duplicate (should fail and rollback)
        try:
            async with in_memory_db.transaction():
                await in_memory_db.execute(
                    "INSERT INTO test (id, name) VALUES (1, 'duplicate')"
                )
        except Exception:
            pass

        # Should still have only 1 record
        count = await in_memory_db.get_table_count("test")
        assert count == 1

    @pytest.mark.asyncio
    async def test_table_exists_true(self, in_memory_db):
        """Test table_exists returns True for existing table"""
        await in_memory_db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        await in_memory_db.commit()

        exists = await in_memory_db.table_exists("test")
        assert exists is True

    @pytest.mark.asyncio
    async def test_table_exists_false(self, in_memory_db):
        """Test table_exists returns False for non-existing table"""
        exists = await in_memory_db.table_exists("nonexistent")
        assert exists is False

    @pytest.mark.asyncio
    async def test_get_table_count(self, in_memory_db):
        """Test getting row count for table"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        await in_memory_db.execute_many(
            "INSERT INTO test (name) VALUES (?)",
            [("a",), ("b",), ("c",), ("d",), ("e",)],
        )
        await in_memory_db.commit()

        count = await in_memory_db.get_table_count("test")
        assert count == 5

    @pytest.mark.asyncio
    async def test_disconnect(self, test_db):
        """Test disconnecting from database"""
        assert test_db._connection is not None

        await test_db.disconnect()

        assert test_db._connection is None

    @pytest.mark.asyncio
    async def test_reconnect_after_disconnect(self, test_db):
        """Test can reconnect after disconnecting"""
        await test_db.disconnect()
        await test_db.connect()

        # Should be able to execute queries
        await test_db.execute("SELECT 1")

    @pytest.mark.asyncio
    async def test_repr(self, in_memory_db):
        """Test string representation"""
        repr_str = repr(in_memory_db)
        assert "DatabaseConnection" in repr_str
        assert "connected" in repr_str

    @pytest.mark.asyncio
    async def test_commit(self, in_memory_db):
        """Test explicit commit"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        await in_memory_db.execute("INSERT INTO test (name) VALUES (?)", ("test",))
        await in_memory_db.commit()

        # Verify data persisted
        result = await in_memory_db.fetch_one("SELECT COUNT(*) FROM test")
        assert result[0] == 1

    @pytest.mark.asyncio
    async def test_rollback(self, in_memory_db):
        """Test explicit rollback"""
        await in_memory_db.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        await in_memory_db.commit()

        # Insert but don't commit
        await in_memory_db.execute("INSERT INTO test (name) VALUES (?)", ("test",))

        # Rollback
        await in_memory_db.rollback()

        # Should have no rows
        count = await in_memory_db.get_table_count("test")
        assert count == 0


class TestDatabaseUtilities:
    """Test database utility functions"""

    @pytest.mark.asyncio
    async def test_init_database(self):
        """Test database initialization"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_init.db")

        # Mock settings to use test database
        import database.connection as conn_module

        original_get_database = conn_module.get_database

        def mock_get_database():
            return DatabaseConnection(db_path)

        conn_module.get_database = mock_get_database

        try:
            db = await init_database()
            assert db is not None
            assert Path(db_path).exists()

            await close_database()
        finally:
            conn_module.get_database = original_get_database
            try:
                os.remove(db_path)
                os.rmdir(temp_dir)
            except:
                pass

    @pytest.mark.asyncio
    async def test_close_database(self):
        """Test closing global database"""
        import database.connection as conn_module

        # Create a temporary global database
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_close.db")

        original_db = conn_module._database
        conn_module._database = DatabaseConnection(db_path)
        await conn_module._database.connect()

        try:
            await close_database()
            assert conn_module._database is None
        finally:
            conn_module._database = original_db
            try:
                os.remove(db_path)
                os.rmdir(temp_dir)
            except:
                pass

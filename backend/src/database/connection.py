"""
Database Connection Management
Provides async SQLite database connection utilities and context managers
"""

import aiosqlite
import asyncio
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager
import logging

from config import get_settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Manages SQLite database connections with async support
    Provides connection pooling and context management
    """

    def __init__(self, database_path: str):
        """
        Initialize database connection manager

        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = Path(database_path)
        self._connection: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> aiosqlite.Connection:
        """
        Establish connection to the database
        Creates the database file if it doesn't exist

        Returns:
            aiosqlite.Connection: Active database connection
        """
        async with self._lock:
            if self._connection is None:
                # Ensure parent directory exists
                self.database_path.parent.mkdir(parents=True, exist_ok=True)

                # Connect to database
                self._connection = await aiosqlite.connect(
                    str(self.database_path),
                    timeout=30.0,
                )

                # Enable foreign key constraints
                await self._connection.execute("PRAGMA foreign_keys = ON")

                # Set journal mode to WAL for better concurrency
                await self._connection.execute("PRAGMA journal_mode = WAL")

                # Commit pragma settings
                await self._connection.commit()

                logger.info(f"Connected to database: {self.database_path}")

            return self._connection

    async def disconnect(self):
        """
        Close the database connection
        """
        async with self._lock:
            if self._connection is not None:
                await self._connection.close()
                self._connection = None
                logger.info("Database connection closed")

    async def get_connection(self) -> aiosqlite.Connection:
        """
        Get active database connection, creating one if necessary

        Returns:
            aiosqlite.Connection: Active database connection
        """
        if self._connection is None:
            await self.connect()
        return self._connection

    @asynccontextmanager
    async def transaction(self):
        """
        Context manager for database transactions
        Automatically commits on success, rolls back on error

        Usage:
            async with db.transaction():
                await db.execute("INSERT INTO ...", ...)
        """
        conn = await self.get_connection()
        try:
            await conn.execute("BEGIN")
            yield conn
            await conn.commit()
        except Exception as e:
            await conn.rollback()
            logger.error(f"Transaction failed, rolling back: {e}")
            raise

    async def execute(self, query: str, parameters=None):
        """
        Execute a single SQL statement

        Args:
            query: SQL query string
            parameters: Query parameters (optional)

        Returns:
            Cursor object
        """
        conn = await self.get_connection()
        if parameters:
            return await conn.execute(query, parameters)
        return await conn.execute(query)

    async def execute_many(self, query: str, parameters_list):
        """
        Execute a SQL statement with multiple parameter sets

        Args:
            query: SQL query string
            parameters_list: List of parameter tuples

        Returns:
            Cursor object
        """
        conn = await self.get_connection()
        return await conn.executemany(query, parameters_list)

    async def fetch_one(self, query: str, parameters=None):
        """
        Execute query and fetch a single row

        Args:
            query: SQL query string
            parameters: Query parameters (optional)

        Returns:
            Single row as tuple or None
        """
        cursor = await self.execute(query, parameters)
        return await cursor.fetchone()

    async def fetch_all(self, query: str, parameters=None):
        """
        Execute query and fetch all rows

        Args:
            query: SQL query string
            parameters: Query parameters (optional)

        Returns:
            List of rows as tuples
        """
        cursor = await self.execute(query, parameters)
        return await cursor.fetchall()

    async def commit(self):
        """
        Commit current transaction
        """
        conn = await self.get_connection()
        await conn.commit()

    async def rollback(self):
        """
        Rollback current transaction
        """
        conn = await self.get_connection()
        await conn.rollback()

    async def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """
        result = await self.fetch_one(query, (table_name,))
        return result is not None

    async def get_table_count(self, table_name: str) -> int:
        """
        Get row count for a table

        Args:
            table_name: Name of the table

        Returns:
            Number of rows in the table
        """
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = await self.fetch_one(query)
        return result[0] if result else 0

    def __repr__(self) -> str:
        status = "connected" if self._connection else "disconnected"
        return f"DatabaseConnection(path={self.database_path}, status={status})"


# Global database instance
_database: Optional[DatabaseConnection] = None


def get_database() -> DatabaseConnection:
    """
    Get or create global database connection instance
    Uses database path from application settings

    Returns:
        DatabaseConnection: Global database instance
    """
    global _database
    if _database is None:
        settings = get_settings()
        _database = DatabaseConnection(settings.database_path)
    return _database


@asynccontextmanager
async def get_db_connection():
    """
    Dependency for FastAPI that provides database connection
    Ensures connection is properly managed

    Usage in FastAPI endpoint:
        @app.get("/contacts")
        async def get_contacts(db: DatabaseConnection = Depends(get_db_connection)):
            ...
    """
    db = get_database()
    try:
        await db.connect()
        yield db
    finally:
        # Connection is kept alive for reuse
        # Only closed on application shutdown
        pass


async def init_database():
    """
    Initialize database connection and run migrations
    Should be called on application startup
    """
    db = get_database()
    await db.connect()
    logger.info("Database initialized")
    return db


async def close_database():
    """
    Close database connection
    Should be called on application shutdown
    """
    global _database
    if _database is not None:
        await _database.disconnect()
        _database = None

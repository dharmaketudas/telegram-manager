#!/usr/bin/env python3
"""
Migration Management CLI Tool
Provides command-line interface for managing database migrations

Usage:
    python manage_migrations.py status     - Show migration status
    python manage_migrations.py run        - Run pending migrations
    python manage_migrations.py rollback   - Rollback last migration
    python manage_migrations.py info       - Show database info
    python manage_migrations.py reset      - Reset database (WARNING: deletes all data)
"""

import sys
import asyncio
from pathlib import Path

# Add src directory to Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from database import (
    get_database,
    run_migrations,
    get_migration_status,
    get_database_stats,
    reset_database,
)
from database.migrations import get_migration_manager


async def show_status():
    """Show status of all migrations"""
    db = get_database()
    await db.connect()

    print("\n" + "=" * 70)
    print(" MIGRATION STATUS")
    print("=" * 70 + "\n")

    status = await get_migration_status(db)

    if not status:
        print("No migrations registered.\n")
    else:
        for m in status:
            symbol = "✓" if m["applied"] else "✗"
            print(f"{symbol} Version {m['version']}: {m['name']}")
            print(f"  Description: {m['description']}")
            if m["applied"]:
                print(f"  Applied at: {m['applied_at']}")
            else:
                print(f"  Status: PENDING")
            print()

    # Count stats
    applied = sum(1 for m in status if m["applied"])
    pending = sum(1 for m in status if not m["applied"])

    print("-" * 70)
    print(f"Total migrations: {len(status)}")
    print(f"Applied: {applied} | Pending: {pending}")
    print("-" * 70 + "\n")

    await db.disconnect()


async def run_pending_migrations():
    """Run all pending migrations"""
    db = get_database()
    await db.connect()

    print("\n" + "=" * 70)
    print(" RUNNING MIGRATIONS")
    print("=" * 70 + "\n")

    success = await run_migrations(db)

    if success:
        print("\n✓ All migrations completed successfully!\n")
    else:
        print("\n✗ Migration failed. Check logs for details.\n")

    await db.disconnect()
    return success


async def rollback_migration():
    """Rollback the last applied migration"""
    db = get_database()
    await db.connect()

    print("\n" + "=" * 70)
    print(" ROLLBACK MIGRATION")
    print("=" * 70 + "\n")

    # Check if there are any migrations to rollback
    row = await db.fetch_one(
        "SELECT version, name FROM _migrations ORDER BY applied_at DESC LIMIT 1"
    )

    if not row:
        print("No migrations to rollback.\n")
        await db.disconnect()
        return

    version, name = row
    print(f"Rolling back migration: {version} - {name}\n")

    confirm = input("Are you sure? This will undo the migration. (yes/no): ")
    if confirm.lower() != "yes":
        print("Rollback cancelled.\n")
        await db.disconnect()
        return

    manager = get_migration_manager(db)
    success = await manager.rollback_last_migration()

    if success:
        print("\n✓ Rollback successful!\n")
    else:
        print("\n✗ Rollback failed. Check logs for details.\n")

    await db.disconnect()


async def show_database_info():
    """Show database information and statistics"""
    db = get_database()
    await db.connect()

    print("\n" + "=" * 70)
    print(" DATABASE INFORMATION")
    print("=" * 70 + "\n")

    # Database file info
    print(f"Database: {db.database_path}")
    if db.database_path.exists():
        size_bytes = db.database_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        print(f"Size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
    else:
        print("Status: Database file does not exist")

    print()

    # Table statistics
    stats = await get_database_stats(db)

    print("Table Row Counts:")
    print("-" * 70)
    for table, count in stats.items():
        if count >= 0:
            print(f"  {table:<20} {count:>10,} rows")
        else:
            print(f"  {table:<20} {'ERROR':>10}")
    print()

    # Migration info
    try:
        result = await db.fetch_one("SELECT COUNT(*) FROM _migrations")
        migration_count = result[0] if result else 0
        print(f"Applied migrations: {migration_count}")

        if migration_count > 0:
            result = await db.fetch_one(
                "SELECT version, name, applied_at FROM _migrations ORDER BY applied_at DESC LIMIT 1"
            )
            if result:
                version, name, applied_at = result
                print(f"Latest migration: {version} - {name}")
                print(f"Applied at: {applied_at}")
    except Exception as e:
        print(f"Could not fetch migration info: {e}")

    print()

    # Schema version
    try:
        result = await db.fetch_one(
            "SELECT value FROM session_config WHERE key = 'schema_version'"
        )
        if result:
            print(f"Schema version: {result[0]}")
    except Exception:
        print("Schema version: Not set")

    print()
    print("=" * 70 + "\n")

    await db.disconnect()


async def reset_database_with_confirmation():
    """Reset database after confirmation"""
    db = get_database()
    await db.connect()

    print("\n" + "=" * 70)
    print(" RESET DATABASE")
    print("=" * 70 + "\n")

    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print("⚠️  All tables will be dropped and recreated.\n")

    confirm1 = input("Type 'DELETE ALL DATA' to confirm: ")
    if confirm1 != "DELETE ALL DATA":
        print("Reset cancelled.\n")
        await db.disconnect()
        return

    confirm2 = input("Are you absolutely sure? (yes/no): ")
    if confirm2.lower() != "yes":
        print("Reset cancelled.\n")
        await db.disconnect()
        return

    print("\nResetting database...\n")

    success = await reset_database(db)

    if success:
        print("\n✓ Database reset complete!\n")
    else:
        print("\n✗ Database reset failed. Check logs for details.\n")

    await db.disconnect()


def print_usage():
    """Print usage information"""
    print("\nMigration Management CLI")
    print("=" * 70)
    print("\nUsage: python manage_migrations.py <command>")
    print("\nCommands:")
    print("  status     Show migration status")
    print("  run        Run pending migrations")
    print("  rollback   Rollback last migration")
    print("  info       Show database information")
    print("  reset      Reset database (WARNING: deletes all data)")
    print("  help       Show this help message")
    print("\nExamples:")
    print("  python manage_migrations.py status")
    print("  python manage_migrations.py run")
    print("  python manage_migrations.py info")
    print()


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "status":
            await show_status()
        elif command == "run":
            success = await run_pending_migrations()
            sys.exit(0 if success else 1)
        elif command == "rollback":
            await rollback_migration()
        elif command == "info":
            await show_database_info()
        elif command == "reset":
            await reset_database_with_confirmation()
        elif command in ["help", "-h", "--help"]:
            print_usage()
        else:
            print(f"\n✗ Unknown command: {command}\n")
            print_usage()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

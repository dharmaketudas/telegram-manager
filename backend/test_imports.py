#!/usr/bin/env python3
"""
Quick Import Test Script
Tests that all imports work correctly after the import fix
"""

import sys
from pathlib import Path

# Add src directory to Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

print("Testing imports after fix...")
print("=" * 60)

try:
    print("✓ Testing config import...", end=" ")
    from config import get_settings, Settings

    print("SUCCESS")
except ImportError as e:
    print(f"FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Testing database.connection import...", end=" ")
    from database.connection import DatabaseConnection, get_database

    print("SUCCESS")
except ImportError as e:
    print(f"FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Testing database.migrations import...", end=" ")
    from database.migrations import create_tables, run_migrations

    print("SUCCESS")
except ImportError as e:
    print(f"FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Testing database package import...", end=" ")
    from database import init_database, close_database

    print("SUCCESS")
except ImportError as e:
    print(f"FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Testing main module import...", end=" ")
    import main

    print("SUCCESS")
except ImportError as e:
    print(f"FAILED: {e}")
    sys.exit(1)

print("=" * 60)
print("✅ All imports successful! The import fix is working correctly.")
print("\nYou can now run:")
print("  python start.py         # To start the server")
print("  pytest                   # To run tests")
print("  ./run_tests.sh          # To run tests with script")

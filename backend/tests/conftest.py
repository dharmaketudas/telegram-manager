"""
Pytest Configuration
Configures Python path and provides common fixtures for tests
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path so tests can import modules
backend_dir = Path(__file__).parent.parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

# Configure pytest
import pytest
import asyncio


# Configure event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Set environment variables for testing
os.environ["DATABASE_PATH"] = ":memory:"
os.environ["API_ID"] = "12345"
os.environ["API_HASH"] = "test_hash"
os.environ["PHONE"] = "+1234567890"

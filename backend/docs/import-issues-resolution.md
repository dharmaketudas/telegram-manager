# Import Issues Resolution Guide

Complete guide to resolving and preventing import errors in the Telegram Contact Manager backend.

---

## Overview

This document covers all import-related issues encountered during development, their solutions, and best practices to prevent them in the future.

---

## Common Import Issues

### Issue 1: Relative Import Errors

**Error Message:**
```
ImportError: attempted relative import with no known parent package
```

**When It Occurs:**
When running a module directly that contains relative imports:

```bash
python src/main.py  # ❌ Fails with relative imports
```

**Why It Happens:**
Python treats directly executed files as `__main__` rather than as part of a package, making relative imports (`.module`, `..module`) fail.

**Solution:**
Use the `start.py` launcher script which properly configures the Python path:

```bash
python start.py  # ✅ Works correctly
```

**How start.py Works:**
```python
# start.py
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Now imports work correctly
from main import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### Issue 2: Missing Module Exports

**Error Message:**
```
ImportError: cannot import name 'init_database' from 'database'
Did you mean: 'get_database'?
```

**When It Occurs:**
When trying to import functions that exist in submodules but aren't exported from the package's `__init__.py`:

```python
from database import init_database  # ❌ Not exported
```

**Why It Happens:**
The function exists in `database/connection.py` but isn't listed in `database/__init__.py`, so it's not available at the package level.

**Solution:**
Update `__init__.py` to export the function:

```python
# database/__init__.py
from .connection import DatabaseConnection, get_database, init_database, close_database
from .migrations import create_tables, run_migrations, verify_schema

__all__ = [
    "DatabaseConnection",
    "get_database",
    "init_database",      # ✅ Now exported
    "close_database",     # ✅ Now exported
    "create_tables",
    "run_migrations",
    "verify_schema",      # ✅ Now exported
]
```

---

### Issue 3: Module Not Found

**Error Message:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**When It Occurs:**
When dependencies aren't installed or virtual environment isn't activated.

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, telethon, aiosqlite; print('✅ All installed!')"
```

---

### Issue 4: Circular Import Errors

**Error Message:**
```
ImportError: cannot import name 'X' from partially initialized module 'Y'
(most likely due to a circular import)
```

**When It Occurs:**
When modules import each other directly or indirectly:

```python
# module_a.py
from module_b import something  # module_b imports module_a

# module_b.py
from module_a import other_thing  # Circular dependency!
```

**Solution:**
1. **Reorganize imports** - Move shared code to a third module
2. **Use local imports** - Import inside functions instead of at module level
3. **Use forward references** - For type hints, use string literals

```python
# ✅ Solution 1: Third module
# shared.py
class SharedClass:
    pass

# module_a.py
from shared import SharedClass

# module_b.py
from shared import SharedClass

# ✅ Solution 2: Local import
def my_function():
    from module_b import something  # Import when needed
    return something()

# ✅ Solution 3: Forward reference (type hints only)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from module_b import SomeClass

def process(item: 'SomeClass'):  # String literal
    pass
```

---

## Historical Issues & Resolutions

### Problem 1: Relative vs Absolute Imports (Resolved)

**Original Issue:**
The codebase used relative imports which failed when running files directly:

```python
# src/main.py (old)
from .database import init_database  # ❌ Relative import
from .config import get_settings      # ❌ Relative import
```

**Solution Applied:**
1. Changed to absolute imports throughout codebase
2. Created `start.py` to configure Python path
3. Updated all import statements

```python
# src/main.py (new)
from database import init_database  # ✅ Absolute import
from config import get_settings      # ✅ Absolute import
```

**Files Modified:**
- `src/main.py`
- `src/database/connection.py`
- `tests/unit/test_database_connection.py`
- `tests/unit/test_database_migrations.py`

**Result:** ✅ All imports work correctly

---

### Problem 2: Missing __init__.py Exports (Resolved)

**Original Issue:**
Functions existed but weren't exported at package level:

```python
# database/__init__.py (old)
from .connection import DatabaseConnection, get_database
from .migrations import create_tables, run_migrations
# Missing: init_database, close_database, verify_schema
```

**Solution Applied:**
Added missing exports to `__init__.py`:

```python
# database/__init__.py (new)
from .connection import DatabaseConnection, get_database, init_database, close_database
from .migrations import create_tables, run_migrations, verify_schema

__all__ = [
    "DatabaseConnection",
    "get_database",
    "init_database",
    "close_database",
    "create_tables",
    "run_migrations",
    "verify_schema",
]
```

**Result:** ✅ All functions accessible via package import

---

## Current Import Structure

### Correct Import Pattern

```python
# ✅ Importing from packages
from database import get_database, init_database, close_database
from database import create_tables, run_migrations, verify_schema
from config import get_settings

# ✅ Importing specific classes/functions
from database.connection import DatabaseConnection
from database.migrations import Migration

# ✅ Type imports
from typing import Optional, List
```

### Package Structure

```
src/
├── __init__.py
├── main.py              # FastAPI app
├── config.py            # Configuration
├── database/
│   ├── __init__.py      # Exports public API
│   ├── connection.py    # DatabaseConnection class
│   ├── migrations.py    # Legacy migration support
│   └── migrations/      # Migration system
│       ├── __init__.py
│       └── migration_*.py
├── models/              # Domain models
├── repositories/        # Data access
├── services/            # Business logic
└── api/                 # API routes
```

---

## Running the Application

### ✅ Correct Methods

**Method 1: Using start.py (Recommended)**
```bash
python start.py
```

**Method 2: Using uvicorn from src directory**
```bash
cd src
uvicorn main:app --reload
```

**Method 3: Using shell script**
```bash
./run.sh
```

### ❌ Incorrect Methods

**Don't run main.py directly:**
```bash
python src/main.py        # ❌ Import errors
python -m src.main        # ❌ May cause issues
cd src && python main.py  # ❌ Import errors
```

---

## Testing

### Running Tests

**✅ Correct:**
```bash
# From backend directory
pytest
./run_tests.sh
pytest -v
pytest --cov=src
```

**Test Configuration:**
The `tests/conftest.py` file configures the Python path automatically:

```python
# tests/conftest.py
import sys
from pathlib import Path

# Add src to path for tests
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
```

---

## Troubleshooting Guide

### Step 1: Verify Virtual Environment

```bash
# Check if activated
which python  # Should show venv/bin/python

# If not activated, activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Step 2: Verify Dependencies

```bash
# Check if dependencies are installed
pip list | grep fastapi
pip list | grep telethon
pip list | grep aiosqlite

# If missing, install
pip install -r requirements.txt
```

### Step 3: Test Imports

```bash
# Quick import test
python test_imports.py

# Or manually
python -c "
import sys
sys.path.insert(0, 'src')
from database import get_database, init_database
from config import get_settings
print('✅ All imports successful')
"
```

### Step 4: Check Python Path

```bash
# Print Python path
python -c "import sys; print('\n'.join(sys.path))"

# Should include:
# - /path/to/backend/src (when using start.py)
# - /path/to/backend/venv/lib/python3.x/site-packages
```

### Step 5: Verify File Structure

```bash
# Check that all __init__.py files exist
find src -name "__init__.py"

# Should show:
# src/__init__.py
# src/database/__init__.py
# src/database/migrations/__init__.py
# etc.
```

---

## Prevention Strategies

### 1. Use Consistent Import Style

**Choose one style and stick with it:**

```python
# ✅ Absolute imports (our choice)
from database import get_database
from config import get_settings

# ❌ Don't mix with relative imports
from .database import get_database  # Don't do this
```

### 2. Always Export Public Functions

**In every `__init__.py`, explicitly export public API:**

```python
# package/__init__.py
from .module_a import function_a, ClassA
from .module_b import function_b, ClassB

__all__ = [
    "function_a",
    "ClassA",
    "function_b",
    "ClassB",
]
```

### 3. Use Type Checking Guards

**Prevent circular imports in type hints:**

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from some_module import SomeClass

def function(arg: 'SomeClass'):  # String literal
    pass
```

### 4. Test Imports in CI/CD

**Add import verification to your test suite:**

```python
# tests/test_imports.py
def test_database_imports():
    """Verify all database functions can be imported"""
    from database import (
        get_database,
        init_database,
        close_database,
        run_migrations,
        verify_schema,
    )
    assert get_database is not None
    assert init_database is not None
```

### 5. Use Import Checker Tools

```bash
# Install tools
pip install pylint mypy

# Check for import issues
pylint src/
mypy src/

# Add to pre-commit hooks
```

---

## Quick Reference

### Import Checklist

Before committing code, verify:

- [ ] All imports are absolute (not relative)
- [ ] New functions are exported in `__init__.py`
- [ ] `__all__` is updated if needed
- [ ] Virtual environment is activated
- [ ] `pytest` runs without import errors
- [ ] `python test_imports.py` succeeds

### Common Commands

```bash
# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test imports
python test_imports.py

# Run application
python start.py

# Run tests
pytest

# Check for issues
python -c "from database import get_database; print('OK')"
```

---

## Error Message Reference

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| `attempted relative import` | Running file directly with relative imports | Use `python start.py` |
| `cannot import name 'X' from 'Y'` | Function not exported in `__init__.py` | Add to exports |
| `No module named 'X'` | Dependency not installed | Run `pip install -r requirements.txt` |
| `circular import` | Modules import each other | Reorganize imports or use TYPE_CHECKING |
| `ModuleNotFoundError: 'src'` | Wrong working directory | Run from backend/ directory |

---

## Additional Resources

### Documentation
- [Getting Started Guide](./getting-started.md)
- [Setup & Configuration](./setup-and-configuration.md)
- [Development Workflow](./development-workflow.md)

### Python Import System
- [Python Import System](https://docs.python.org/3/reference/import.html)
- [Python Packages](https://docs.python.org/3/tutorial/modules.html#packages)
- [PEP 420 - Implicit Namespace Packages](https://www.python.org/dev/peps/pep-0420/)

---

## Summary

### Issues Resolved ✅

1. ✅ Relative import errors - Fixed with absolute imports
2. ✅ Missing exports - Updated all `__init__.py` files
3. ✅ Module not found - Dependencies installed
4. ✅ Import structure - Consistent pattern throughout

### Current Status

- **Import System:** ✅ Working correctly
- **Test Suite:** ✅ All tests passing (70+)
- **Application Startup:** ✅ No import errors
- **Documentation:** ✅ Complete and accurate

### Prevention in Place

- ✅ Absolute imports used consistently
- ✅ All public APIs properly exported
- ✅ `start.py` handles path configuration
- ✅ Tests verify import functionality
- ✅ Documentation updated

**All import issues have been resolved and preventive measures are in place.** ✅

---

**For additional help, see the [Getting Started Guide](./getting-started.md) or [Troubleshooting Section](./setup-and-configuration.md#troubleshooting).**
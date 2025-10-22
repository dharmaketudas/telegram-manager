# Getting Started Guide

Get the Telegram Contact Manager backend up and running in 5 minutes.

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.9 or higher** - Check with `python3 --version`
- **pip** - Python package installer (usually comes with Python)
- **A Telegram account** with phone number
- **Telegram API credentials** - Get from https://my.telegram.org/apps

### Getting Your Telegram API Credentials

1. Visit https://my.telegram.org/apps
2. Log in with your Telegram account
3. Fill out the form to create a new application
4. Save your `api_id` and `api_hash` - you'll need these for configuration

---

## Quick Installation

### Step 1: Navigate to Backend Directory

```bash
cd telegram-manager/backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Verify installation:**
```bash
python -c "import fastapi, telethon, aiosqlite; print('✅ All dependencies installed!')"
```

---

## Configuration

### Step 1: Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Edit Configuration

Open `.env` in your favorite editor and add your credentials:

```bash
nano .env  # or use your preferred editor
```

**Required configuration:**
```env
# Get these from https://my.telegram.org/apps
API_ID=your_api_id_here
API_HASH=your_api_hash_here
PHONE=+1234567890  # Your phone number in international format with +
```

**Optional configuration (defaults provided):**
```env
# Database
DATABASE_PATH=./data/contacts.db

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# CORS (for frontend development)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

---

## Running the Application

### Option 1: Using the Startup Script (Recommended)

```bash
python start.py
```

### Option 2: Using the Shell Script

```bash
./run.sh
```

### Option 3: Using Uvicorn Directly

```bash
cd src
uvicorn main:app --reload --port 8000
```

### Expected Output

When the server starts successfully, you should see:

```
Starting Telegram Contact Manager API on 0.0.0.0:8000
API Documentation: http://localhost:8000/docs
Press CTRL+C to stop the server

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting Telegram Contact Manager API...
INFO:     Data directories created/verified
INFO:     Connected to database: data/contacts.db
INFO:     Database initialized
INFO:     Running database migrations...
INFO:     Created table: contacts
INFO:     Created table: groups
INFO:     Created table: tags
INFO:     Created table: contact_tags
INFO:     Created table: contact_groups
INFO:     Created table: messages
INFO:     Created table: session_config
INFO:     Created table: sync_log
INFO:     Database migrations completed successfully
INFO:     Database schema verification passed
INFO:     Application started successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Verify Installation

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status":"healthy","message":"API is running"}
```

### 2. API Information

```bash
curl http://localhost:8000/
```

**Expected response:**
```json
{
  "name": "Telegram Contact Manager API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

### 3. Interactive API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation for all API endpoints.

---

## Running Tests

Verify everything works by running the test suite:

```bash
# Run all tests
pytest

# Or use the test script
./run_tests.sh

# Run with verbose output
pytest -v

# Run with coverage
./run_tests.sh coverage
```

**Expected result:** All 70+ tests should pass ✅

---

## First-Time Setup Flow

Now that the backend is running, here's what to do next:

1. **Start the backend server** (you just did this!)
2. **Open the API documentation** at http://localhost:8000/docs
3. **Initialize authentication**:
   - Use the `/api/auth/init` endpoint
   - Provide your API credentials and phone number
4. **Enter verification code**:
   - Check Telegram for the verification code
   - Submit it via `/api/auth/code` endpoint
5. **Enter 2FA password** (if you have 2FA enabled)
6. **Sync contacts**:
   - Trigger initial sync with `/api/sync/contacts`
7. **Start using the API**:
   - Browse contacts
   - Create tags
   - Send messages

---

## Common Commands

Keep these handy for daily development:

```bash
# Start server
python start.py

# Run tests
pytest

# Run tests with coverage
./run_tests.sh coverage

# Check imports
python test_imports.py

# View logs (if logging to file)
tail -f logs/app.log
```

---

## Troubleshooting

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

**Error:** `[Errno 48] Address already in use`

**Solution 1:** Kill the existing process:
```bash
# Find the process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Solution 2:** Change the port in `.env`:
```env
API_PORT=8001
```

### Permission Denied on Scripts

**Error:** `Permission denied: ./run.sh`

**Solution:**
```bash
chmod +x run.sh
chmod +x run_tests.sh
```

### Database Locked Error

**Error:** `sqlite3.OperationalError: database is locked`

**Solution:**
1. Make sure only one instance of the backend is running
2. Close any database browser tools
3. Delete lock files if they exist:
```bash
rm data/contacts.db-wal data/contacts.db-shm
```

### Can't Connect to Database

**Solution:**
```bash
# Ensure data directory exists
mkdir -p data/sessions data/media

# Check permissions
chmod -R 755 data/
```

---

## Project Structure

Understanding where things are:

```
backend/
├── start.py              # Application launcher (use this to start)
├── src/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration management
│   └── database/        # Database layer
│       ├── connection.py   # Connection management
│       ├── migrations.py   # Legacy migrations
│       └── migrations/     # Migration system
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── data/               # Runtime data (auto-created)
│   ├── contacts.db     # SQLite database
│   ├── sessions/       # Telegram sessions
│   └── media/          # Downloaded media
├── docs/               # Documentation (you are here)
├── requirements.txt    # Python dependencies
└── .env               # Configuration (create from .env.example)
```

---

## What's Next?

Now that you have the backend running:

### Explore the API
- Open http://localhost:8000/docs
- Try out the endpoints using the interactive documentation
- Understand the available operations

### Learn the Database
- Review the [Database Schema](./database-schema.md)
- Understand the tables and relationships
- Learn about the migration system

### Start Development
- Read the [Development Workflow](./development-workflow.md)
- Understand how to add features
- Learn the testing process

### Connect the Frontend
- Set up the frontend application
- Configure it to connect to this backend
- Start building features

---

## Quick Reference

### Access Points

| What | URL |
|------|-----|
| API Base | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

### Essential Files

| File | Purpose |
|------|---------|
| `start.py` | Start the application |
| `.env` | Configuration |
| `src/main.py` | FastAPI app |
| `requirements.txt` | Dependencies |
| `pytest.ini` | Test configuration |

### Important Commands

```bash
python start.py           # Start server
pytest                    # Run tests
./run_tests.sh coverage  # Tests with coverage
python test_imports.py   # Verify imports
```

---

## Security Reminder

⚠️ **Never commit these files to version control:**
- `.env` - Contains your API credentials
- `data/sessions/*.session` - Contains auth tokens
- `data/contacts.db` - Contains your contact data

These files should be listed in `.gitignore`.

---

## Getting Help

Need more information?

- **Detailed Setup**: See [Setup & Configuration](./setup-and-configuration.md)
- **Database Info**: See [Database Schema](./database-schema.md)
- **Troubleshooting**: See [Import Issues Resolution](./import-issues-resolution.md)
- **API Reference**: http://localhost:8000/docs (when server is running)
- **Migration Help**: See [Migration Quick Reference](./migrations-quick-reference.md)

---

**You're ready to go! 🚀**

The Telegram Contact Manager backend is now running and ready for development.
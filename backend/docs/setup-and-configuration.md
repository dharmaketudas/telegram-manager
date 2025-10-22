# Setup and Configuration Guide

Complete guide for setting up and configuring the Telegram Contact Manager backend.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Verification](#verification)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Python 3.9 or higher**
  - Check your version: `python3 --version`
  - Download from: https://www.python.org/downloads/

- **pip** (Python package installer)
  - Usually comes with Python
  - Verify: `pip --version`

- **Git** (recommended)
  - For cloning the repository
  - Download from: https://git-scm.com/

### Telegram Requirements

- **Active Telegram account**
  - Must have a phone number associated
  - Account should be accessible via mobile or desktop app

- **Telegram API Credentials**
  - Required: `api_id` and `api_hash`
  - Obtain from: https://my.telegram.org/apps

### Obtaining Telegram API Credentials

1. **Visit the API Development Tools page**
   - Go to: https://my.telegram.org/apps
   
2. **Log in to your Telegram account**
   - Use your phone number
   - Enter the verification code sent to your Telegram app
   
3. **Fill out the application form**
   - App title: Any name (e.g., "My Contact Manager")
   - Short name: Short identifier (e.g., "contact_mgr")
   - Platform: Choose appropriate platform or "Other"
   - Description: Brief description of your use case
   
4. **Save your credentials**
   - Copy your `api_id` (numeric value)
   - Copy your `api_hash` (alphanumeric string)
   - ⚠️ Keep these secure - never commit to version control

---

## Installation

### Step 1: Navigate to Project Directory

```bash
cd telegram-manager/backend
```

### Step 2: Create Virtual Environment

Creating a virtual environment isolates the project dependencies from your system Python.

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your prompt should now show (venv)
```

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Your prompt should now show (venv)
```

**Verify activation:**
```bash
which python  # Should point to venv/bin/python (macOS/Linux)
where python  # Should point to venv\Scripts\python (Windows)
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**Expected packages installed:**
- fastapi - Web framework
- uvicorn - ASGI server
- telethon - Telegram client library
- aiosqlite - Async SQLite database
- pydantic - Data validation
- python-dotenv - Environment variable management
- pillow - Image processing
- pytest - Testing framework (dev)
- pytest-asyncio - Async test support (dev)
- pytest-cov - Test coverage (dev)

**Verify installation:**
```bash
python -c "import fastapi, telethon, aiosqlite; print('✅ All core dependencies installed!')"
```

### Step 4: Create Required Directories

The application will create these automatically, but you can create them manually:

```bash
mkdir -p data/sessions data/media
```

---

## Configuration

### Environment Variables

Configuration is managed through environment variables stored in a `.env` file.

### Step 1: Create Environment File

```bash
# Copy the example file
cp .env.example .env
```

If `.env.example` doesn't exist, create `.env` manually:

```bash
touch .env
```

### Step 2: Configure Required Variables

Open `.env` in your editor:

```bash
nano .env
# or
vim .env
# or use any text editor
```

Add the following **required** configuration:

```env
# Telegram API Credentials (REQUIRED)
# Get these from https://my.telegram.org/apps
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
PHONE=+1234567890

# Note: Replace with your actual values
# PHONE must be in international format with + prefix
```

### Configuration Options Reference

#### Required Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Your Telegram API ID | `12345678` |
| `API_HASH` | Your Telegram API hash | `abcdef123...` |
| `PHONE` | Your phone number | `+1234567890` |

#### Optional Settings - Database

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_PATH` | Path to SQLite database | `./data/contacts.db` |

#### Optional Settings - API Server

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | Host to bind to | `0.0.0.0` |
| `API_PORT` | Port to listen on | `8000` |

#### Optional Settings - Paths

| Variable | Description | Default |
|----------|-------------|---------|
| `MEDIA_PATH` | Directory for downloaded media | `./data/media` |
| `SESSION_PATH` | Directory for Telegram sessions | `./data/sessions` |
| `SESSION_NAME` | Session file name | `telegram_session` |

#### Optional Settings - CORS

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:5173,http://localhost:3000` |

#### Optional Settings - Logging

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging verbosity | `INFO` |

**Available log levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

### Complete .env Example

```env
# Telegram API Credentials (REQUIRED)
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
PHONE=+1234567890

# Database Configuration
DATABASE_PATH=./data/contacts.db

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Paths
MEDIA_PATH=./data/media
SESSION_PATH=./data/sessions
SESSION_NAME=telegram_session

# CORS Configuration (for frontend)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=INFO
```

---

## Running the Application

### Method 1: Using start.py (Recommended)

This is the easiest and recommended way to start the application:

```bash
python start.py
```

**What this does:**
- Loads environment variables from `.env`
- Configures Python path correctly
- Starts uvicorn with optimal settings
- Enables auto-reload for development

### Method 2: Using Shell Script

If you're on macOS/Linux, you can use the convenience script:

```bash
./run.sh
```

**First time only:** Make it executable:
```bash
chmod +x run.sh
```

### Method 3: Using Uvicorn Directly

For more control over uvicorn settings:

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment

For production environments:

```bash
# Using start.py (still recommended)
python start.py

# Or with uvicorn and multiple workers
cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Or with gunicorn (install first: pip install gunicorn)
cd src
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Startup Sequence

When the application starts successfully, you'll see:

```
Starting Telegram Contact Manager API on 0.0.0.0:8000
API Documentation: http://localhost:8000/docs
Press CTRL+C to stop the server

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Starting Telegram Contact Manager API...
INFO:     Data directories created/verified
INFO:     Connected to database: data/contacts.db
INFO:     Database initialized
INFO:     Database connection established
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
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Verification

### 1. Verify Server is Running

**Health Check Endpoint:**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status":"healthy","message":"API is running"}
```

**API Info Endpoint:**
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

### 2. Access API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You should see interactive API documentation.

### 3. Verify Database

Check that the database was created:

```bash
ls -lh data/contacts.db
```

Check that tables were created:

```bash
sqlite3 data/contacts.db "SELECT name FROM sqlite_master WHERE type='table';"
```

**Expected output:**
```
contacts
groups
tags
contact_tags
contact_groups
messages
session_config
sync_log
_migrations
```

### 4. Run Test Suite

```bash
# Run all tests
pytest

# Expected output: All tests passed
```

---

## Advanced Configuration

### Custom Database Location

To use a different database location:

```env
DATABASE_PATH=/path/to/custom/location/database.db
```

Ensure the directory exists and is writable:
```bash
mkdir -p /path/to/custom/location
chmod 755 /path/to/custom/location
```

### Multiple Frontend Origins

To allow multiple frontend applications:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080,https://yourdomain.com
```

### Custom Port Configuration

If port 8000 is in use:

```env
API_PORT=8001
```

Then access the API at http://localhost:8001

### Session Management

Configure where Telegram sessions are stored:

```env
SESSION_PATH=./data/sessions
SESSION_NAME=my_custom_session
```

### Logging Configuration

For development (more verbose):
```env
LOG_LEVEL=DEBUG
```

For production (less verbose):
```env
LOG_LEVEL=WARNING
```

---

## Troubleshooting

### Installation Issues

**Issue: pip install fails**

```bash
# Update pip first
pip install --upgrade pip

# Try installing packages individually
pip install fastapi
pip install uvicorn
pip install telethon
# etc.
```

**Issue: Python version too old**

```bash
# Check version
python3 --version

# Install Python 3.9+ from https://www.python.org/downloads/
# Or use pyenv:
pyenv install 3.11
pyenv local 3.11
```

**Issue: Virtual environment activation fails**

```bash
# macOS/Linux: Ensure you have execute permissions
chmod +x venv/bin/activate
source venv/bin/activate

# Windows: Use PowerShell if Command Prompt fails
venv\Scripts\Activate.ps1
```

### Configuration Issues

**Issue: Missing .env file**

```bash
# Create it
touch .env

# Add required variables
echo "API_ID=your_id" >> .env
echo "API_HASH=your_hash" >> .env
echo "PHONE=+1234567890" >> .env
```

**Issue: API credentials not found**

Make sure:
1. `.env` file is in the `backend/` directory (not in `backend/src/`)
2. Variable names are exactly: `API_ID`, `API_HASH`, `PHONE`
3. No quotes around values
4. No spaces around `=`

**Issue: Invalid phone number format**

The phone number must:
- Start with `+`
- Include country code
- Contain only numbers after the `+`

Examples:
- ✅ `+1234567890`
- ✅ `+447700900123`
- ❌ `1234567890` (missing +)
- ❌ `+1 234 567 890` (no spaces)

### Runtime Issues

**Issue: Port already in use**

```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or change the port
echo "API_PORT=8001" >> .env
```

**Issue: Database locked**

```bash
# Stop all running instances
pkill -f "python.*start.py"

# Remove lock files
rm data/contacts.db-wal data/contacts.db-shm

# Restart
python start.py
```

**Issue: Permission denied**

```bash
# Ensure scripts are executable
chmod +x run.sh run_tests.sh

# Ensure data directory is writable
chmod -R 755 data/
```

**Issue: Module not found**

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Telegram Authentication Issues

**Issue: Can't get verification code**

- Check that your phone number is correct in `.env`
- Ensure you can receive messages in Telegram
- Try requesting the code again via the API

**Issue: 2FA password required**

If you have two-factor authentication enabled:
- You'll need to provide your 2FA password
- Use the appropriate API endpoint after entering the code

**Issue: Session expired**

```bash
# Delete old session
rm data/sessions/telegram_session.session

# Restart and authenticate again
python start.py
```

---

## Security Best Practices

### 1. Protect Credentials

**Never commit sensitive files:**
- `.env` - Contains API credentials
- `data/sessions/*.session` - Contains auth tokens
- `data/contacts.db` - Contains personal data

**Verify .gitignore includes:**
```gitignore
.env
*.session
data/
```

### 2. Use Environment-Specific Configuration

Create different `.env` files for different environments:
- `.env.development`
- `.env.production`
- `.env.test`

Load the appropriate one:
```bash
cp .env.production .env
python start.py
```

### 3. Secure Production Deployment

For production:
- Use HTTPS (reverse proxy with nginx/caddy)
- Restrict CORS origins to your domain only
- Use strong passwords for 2FA
- Keep dependencies updated
- Use environment variables or secrets management
- Never expose `.env` file via web server

### 4. Regular Updates

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
pip check
```

---

## Next Steps

Now that your backend is set up and running:

1. **Explore the API** - Visit http://localhost:8000/docs
2. **Read Database Documentation** - See [Database Schema](./database-schema.md)
3. **Learn Development Workflow** - See [Development Workflow](./development-workflow.md)
4. **Set up Frontend** - Connect your frontend application
5. **Start Building Features** - Add your custom functionality

---

## Support Resources

- **Documentation Index**: [INDEX.md](./INDEX.md)
- **Getting Started**: [getting-started.md](./getting-started.md)
- **Database Schema**: [database-schema.md](./database-schema.md)
- **API Docs**: http://localhost:8000/docs (when running)
- **FastAPI**: https://fastapi.tiangolo.com/
- **Telethon**: https://docs.telethon.dev/

---

**Setup complete! Your Telegram Contact Manager backend is ready for development.** 🎉
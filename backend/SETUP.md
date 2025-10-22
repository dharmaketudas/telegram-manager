# Quick Setup Guide

Get the Telegram Contact Manager backend up and running in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- Telegram account
- Telegram API credentials from https://my.telegram.org/apps

## Quick Start

### 1. Install Dependencies

```bash
cd telegram-manager/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

**Minimum required configuration:**
```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
PHONE=+1234567890
```

Get `API_ID` and `API_HASH` from: https://my.telegram.org/apps

### 3. Run the Server

```bash
python start.py
```

The API will start at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs

### 4. Test the API

Open http://localhost:8000/docs in your browser to see the interactive API documentation.

Or test the health endpoint:
```bash
curl http://localhost:8000/health
```

## What's Next?

1. **Authenticate**: Use `/api/auth/init` endpoint to start Telegram authentication
2. **Verify**: Submit the code you receive on Telegram via `/api/auth/code`
3. **Sync Contacts**: Trigger initial sync with `/api/sync/contacts`
4. **Explore**: Browse contacts, create tags, send messages via the API

## Verify Installation

Run this to check everything is working:

```bash
python -c "import fastapi, telethon, aiosqlite; print('✅ All dependencies installed!')"
```

## Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt
```

### Port Already in Use
Change the port in `.env`:
```env
API_PORT=8001
```

### Permission Errors
Ensure data directories are writable:
```bash
chmod -R 755 data/
```

## Development Tips

**Run with auto-reload:**
```bash
python start.py
```

**Run tests:**
```bash
pytest
```

**View logs:**
```bash
tail -f logs/app.log
```

## Need More Help?

- See [README.md](README.md) for comprehensive documentation
- Check [API Docs](http://localhost:8000/docs) when server is running
- Review [design.md](../.claude/specs/contact-management/design.md) for architecture details

## Security Reminder

⚠️ Never commit these files:
- `.env` - Contains your API credentials
- `data/sessions/*.session` - Contains auth tokens
- `data/contacts.db` - Contains your contact data
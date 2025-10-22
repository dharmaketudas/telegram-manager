# Telegram Contact Manager - Backend

Python FastAPI backend for the Telegram Contact Manager application. This service provides a RESTful API for managing Telegram contacts, tags, and bulk messaging capabilities.

## Features

- 🔐 Telegram authentication with 2FA support
- 👥 Automatic contact discovery from all chats and groups
- 🏷️ Contact tagging and organization
- 📨 Bulk messaging by tags
- 📸 Profile and group photo management
- 🔄 Automatic synchronization with Telegram
- 📊 Comprehensive REST API with auto-generated documentation

## Technology Stack

- **Python 3.9+**
- **FastAPI** - Modern async web framework
- **Telethon** - Telegram API client library
- **SQLite** - Embedded database
- **Pydantic** - Data validation and settings management
- **Pillow** - Image processing

## Prerequisites

- Python 3.9 or higher
- Telegram account with phone number
- Telegram API credentials (get from https://my.telegram.org/apps)

## Getting Your Telegram API Credentials

1. Visit https://my.telegram.org/apps
2. Log in with your Telegram account
3. Fill out the form to create a new application
4. Save your `api_id` and `api_hash`

## Installation

### 1. Clone the repository (if not already done)

```bash
cd telegram-manager/backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Create environment file

```bash
cp .env.example .env
```

### 2. Edit the `.env` file with your credentials

```bash
# Required - Get these from https://my.telegram.org/apps
API_ID=your_api_id_here
API_HASH=your_api_hash_here
PHONE=+1234567890

# Optional - Defaults are provided
DATABASE_PATH=./data/contacts.db
MEDIA_PATH=./data/media
SESSION_NAME=telegram_session
```

**Important Configuration Variables:**

- `API_ID` - Your Telegram API ID (required)
- `API_HASH` - Your Telegram API Hash (required)
- `PHONE` - Your phone number in international format with + (required for CLI auth)
- `DATABASE_PATH` - Path to SQLite database file
- `MEDIA_PATH` - Directory for storing profile and group photos
- `SESSION_PATH` - Directory for Telegram session files
- `CORS_ORIGINS` - Allowed origins for CORS (comma-separated)
- `API_PORT` - Port for the API server (default: 8000)

## Running the Application

### Development Mode

```bash
# Make sure you're in the backend directory
cd telegram-manager/backend

# Run with the startup script
python start.py
```

Or using uvicorn directly:

```bash
# Make sure you're in the src directory
cd src
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Production Mode

```bash
# Using the startup script (recommended)
python start.py

# Or with uvicorn from src directory
cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Or with gunicorn:

```bash
cd src
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation for all API endpoints.

### Main API Endpoints

- `POST /api/auth/init` - Initialize authentication
- `POST /api/auth/code` - Submit verification code
- `GET /api/auth/status` - Check authentication status
- `GET /api/contacts` - List all contacts
- `GET /api/contacts/{id}/profile` - Get contact profile
- `POST /api/sync/contacts` - Sync contacts from Telegram
- `GET /api/tags` - List all tags
- `POST /api/tags` - Create a new tag
- `POST /api/contacts/{id}/tags` - Add tag to contact
- `POST /api/messages/send` - Send message to contact
- `POST /api/messages/bulk` - Send bulk message by tags
- `GET /api/media/profile-photos/{filename}` - Get profile photo

## Project Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
├── start.py                 # Application startup script
│   ├── models/              # Domain models (Contact, Tag, etc.)
│   ├── schemas/             # Pydantic schemas for API
│   ├── repositories/        # Database access layer
│   ├── services/            # Business logic
│   ├── telegram/            # Telegram client wrapper
│   ├── database/            # Database connection and migrations
│   └── api/
│       └── routes/          # API endpoint definitions
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── data/
│   ├── contacts.db         # SQLite database (created on first run)
│   ├── sessions/           # Telegram session files
│   └── media/              # Profile and group photos
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration (create from .env.example)
└── README.md              # This file
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_contact_service.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black src/

# Lint with flake8
flake8 src/

# Type checking with mypy
mypy src/
```

## First-Time Setup Flow

1. Start the backend server
2. Open the frontend application (or use API docs)
3. Navigate to authentication page
4. Enter your API credentials (API_ID, API_HASH, Phone)
5. Submit and wait for verification code on Telegram
6. Enter the verification code
7. If 2FA enabled, enter your password
8. Initial contact sync will begin automatically
9. You can now use all features

## Troubleshooting

### "Database is locked" error

This happens when multiple processes try to access SQLite simultaneously. Ensure only one instance of the backend is running.

### Authentication fails

- Verify your API_ID and API_HASH are correct
- Ensure phone number is in international format with + (e.g., +1234567890)
- Check that you received the verification code on Telegram
- For 2FA accounts, ensure you enter the correct password

### Rate limit errors

Telegram has rate limits. The application implements automatic retry with backoff, but if you hit limits frequently:
- Increase `RATE_LIMIT_DELAY` in .env
- Reduce frequency of sync operations
- Avoid sending too many messages in quick succession

### Profile photos not loading

- Check that `MEDIA_PATH` directory exists and is writable
- Verify the backend has permissions to create subdirectories
- Check that photos were downloaded successfully (check logs)

### Port already in use

If port 8000 is already in use, change it in .env:
```bash
API_PORT=8001
```

## Security Notes

- Never commit `.env` file or session files to version control
- Session files contain authentication tokens - keep them secure
- Store API credentials securely
- Use HTTPS in production
- Regularly update dependencies for security patches

## Contributing

When contributing to the backend:

1. Create a new branch for your feature
2. Write tests for new functionality
3. Ensure all tests pass
4. Follow existing code style
5. Update documentation as needed

## License

[Your License Here]

## Support

For issues and questions:
- Check the troubleshooting section above
- Review API documentation at `/docs`
- Check Telethon documentation: https://docs.telethon.dev/
- Review FastAPI documentation: https://fastapi.tiangolo.com/

## Related

- Frontend: `../frontend/`
- Design Document: `../.claude/specs/contact-management/design.md`
- Requirements: `../.claude/specs/contact-management/requirements.md`

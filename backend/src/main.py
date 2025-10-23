"""
Telegram Contact Manager - FastAPI Application
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from pathlib import Path

from src.database.connection import init_database, close_database
from src.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Telegram Contact Manager API",
    description="API for managing Telegram contacts with tagging and bulk messaging capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
# Get allowed origins from environment variable or use defaults
allowed_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for media (profile photos, group photos)
media_path = Path(os.getenv("MEDIA_PATH", "./data/media"))
if media_path.exists():
    app.mount("/api/media", StaticFiles(directory=str(media_path)), name="media")


@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup
    - Create necessary directories
    - Initialize database
    - Run migrations
    - Check configuration
    """
    logger.info("Starting Telegram Contact Manager API...")

    # Get application settings
    settings = get_settings()

    # Create data directories if they don't exist
    media_path = Path("./data/media")
    media_path.mkdir(parents=True, exist_ok=True)
    logger.info("Data directories created/verified")

    # Initialize database connection
    try:
        await init_database()
        logger.info("Database connection established and initialized")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

    logger.info("Application started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on application shutdown
    - Close database connection
    - Cleanup resources
    """
    logger.info("Shutting down Telegram Contact Manager API...")

    try:
        await close_database()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

    logger.info("Shutdown complete")


@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "Telegram Contact Manager API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "API is running"}


# Router includes will be added here as we build out the API
# app.include_router(contacts.router, prefix="/api", tags=["contacts"])
# app.include_router(tags.router, prefix="/api", tags=["tags"])
# app.include_router(messages.router, prefix="/api", tags=["messages"])
# app.include_router(auth.router, prefix="/api", tags=["auth"])
# app.include_router(sync.router, prefix="/api", tags=["sync"])


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    uvicorn.run("main:app", host=host, port=port, reload=True, log_level="info")

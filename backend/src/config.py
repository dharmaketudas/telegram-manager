"""
Application Configuration
Loads and validates configuration from environment variables
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Telegram API Configuration
    api_id: int = Field(default=0, description="Telegram API ID from my.telegram.org")
    api_hash: str = Field(
        default="", description="Telegram API Hash from my.telegram.org"
    )
    phone: str = Field(default="", description="Phone number in international format")

    # Database Configuration
    database_path: str = Field(
        default="./data/contacts.db", description="Path to SQLite database"
    )

    # Media Storage Configuration
    media_path: str = Field(
        default="./data/media", description="Base path for media storage"
    )
    profile_photos_path: str = Field(
        default="./data/media/profile-photos", description="Path for profile photos"
    )
    group_photos_path: str = Field(
        default="./data/media/group-photos", description="Path for group photos"
    )

    # Session Configuration
    session_name: str = Field(
        default="telegram_session", description="Telegram session file name"
    )
    session_path: str = Field(
        default="./data/sessions", description="Path for session files"
    )

    # API Server Configuration
    api_host: str = Field(default="0.0.0.0", description="FastAPI host")
    api_port: int = Field(default=8000, description="FastAPI port")

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Allowed CORS origins (comma-separated)",
    )

    # Rate Limiting
    rate_limit_delay: float = Field(
        default=1.0, description="Delay between API calls in seconds"
    )
    max_retries: int = Field(
        default=3, description="Maximum retry attempts for API calls"
    )

    # Sync Configuration
    sync_interval_minutes: int = Field(
        default=60, description="Automatic sync interval in minutes (0 to disable)"
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("cors_origins")
    def parse_cors_origins(cls, v) -> List[str]:
        """Parse comma-separated CORS origins into a list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("log_level")
    def validate_log_level(cls, v) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v

    def get_session_file_path(self) -> Path:
        """Get full path to the session file"""
        return Path(self.session_path) / f"{self.session_name}.session"

    def ensure_directories_exist(self):
        """Create all necessary directories if they don't exist"""
        directories = [
            self.media_path,
            self.profile_photos_path,
            self.group_photos_path,
            self.session_path,
            str(Path(self.database_path).parent),
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def is_configured(self) -> bool:
        """Check if minimum required configuration is present"""
        return bool(self.api_id and self.api_hash and self.phone)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency function to get settings
    Useful for FastAPI dependency injection
    """
    return settings

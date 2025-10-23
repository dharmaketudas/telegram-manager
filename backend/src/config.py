"""
Configuration settings for the Telegram Contact Manager application.

Provides dynamic configuration loading with support for different
environments and secure settings management.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application configuration settings.

    Manages settings for database, Telegram API, and other application components.
    """

    # Database configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///telegram_manager.db"

    # Telegram API credentials
    API_ID: Optional[str] = None
    API_HASH: Optional[str] = None
    PHONE_NUMBER: Optional[str] = None

    # Logging and debug settings
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # Environment-specific configuration
    ENVIRONMENT: str = "development"

    # Security settings
    SECRET_KEY: str = "test_secret_key_for_local_development"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def database_path(self) -> str:
        """
        Extract database file path from DATABASE_URL.

        For SQLite URLs like sqlite+aiosqlite:///path/to/db.db
        Returns: path/to/db.db
        """
        if ":///" in self.DATABASE_URL:
            # Extract path from URL
            return self.DATABASE_URL.split("///")[1]
        return "telegram_manager.db"


@lru_cache()
def get_settings() -> Settings:
    """
    Retrieve cached application settings.

    Returns:
        Settings: Configured application settings
    """
    return Settings()


def reset_settings_cache():
    """
    Reset the cached settings.

    Useful for testing and dynamic configuration changes.
    """
    get_settings.cache_clear()

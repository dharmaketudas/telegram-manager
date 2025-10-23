"""
Contact SQLAlchemy ORM Model

Defines the database schema and ORM mapping for Contact entities
in the Telegram Contact Manager application.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional

from src.database.base import Base


class Contact(Base):
    """
    SQLAlchemy ORM model representing a Telegram contact.

    Maps the Contact entity to the database, providing a structured
    representation of contact information with SQLAlchemy mappings.
    """

    __tablename__ = "contacts"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Telegram-specific identifiers
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )

    # Personal information
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Media and profile information
    profile_photo_path: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def full_name(self) -> str:
        """
        Generate a full name for the contact.

        Returns:
            str: Concatenated first and last name, or fallback identifiers
        """
        parts = [part for part in [self.first_name, self.last_name] if part]

        if parts:
            return " ".join(parts)
        elif self.username:
            return self.username
        else:
            return f"User {self.telegram_id}"

    def __str__(self) -> str:
        """
        String representation of the contact.

        Returns:
            str: A human-readable contact representation
        """
        return f"Contact({self.full_name}, @{self.username or 'no_username'})"

    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.

        Returns:
            str: A detailed string representation of the contact
        """
        return (
            f"Contact(id={self.id}, "
            f"telegram_id={self.telegram_id}, "
            f"username={self.username}, "
            f"full_name={self.full_name})"
        )

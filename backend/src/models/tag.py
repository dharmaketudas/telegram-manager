"""
Tag SQLAlchemy ORM Model

Defines the database schema and ORM mapping for Tag entities
in the Telegram Contact Manager application.
"""

from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List

from src.database.base import Base


# Association table for many-to-many relationship between contacts and tags
contact_tags = Table(
    "contact_tags",
    Base.metadata,
    Column(
        "contact_id",
        Integer,
        ForeignKey("contacts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("created_at", DateTime, default=datetime.utcnow),
)


class Tag(Base):
    """
    SQLAlchemy ORM model representing a tag for organizing contacts.

    Tags can be assigned to contacts to categorize and filter them.
    Each tag can have a color for visual distinction.
    """

    __tablename__ = "tags"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Tag properties
    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    color: Mapped[Optional[str]] = mapped_column(
        String(7), nullable=True
    )  # Hex color code

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    # Note: We'll use the junction table for queries, but not defining bidirectional
    # relationship here to keep it simple and avoid circular imports

    def __str__(self) -> str:
        """
        String representation of the tag.

        Returns:
            str: A human-readable tag representation
        """
        color_str = f" ({self.color})" if self.color else ""
        return f"Tag({self.name}{color_str})"

    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.

        Returns:
            str: A detailed string representation of the tag
        """
        return (
            f"Tag(id={self.id}, name={self.name}, "
            f"color={self.color}, created_at={self.created_at})"
        )

    def __eq__(self, other) -> bool:
        """
        Compare tags by name (case-insensitive).

        Args:
            other: Another Tag instance

        Returns:
            bool: True if tags have the same name (ignoring case)
        """
        if not isinstance(other, Tag):
            return False
        return self.name.lower() == other.name.lower()

    def __hash__(self) -> int:
        """
        Hash based on lowercase name for use in sets and dicts.

        Returns:
            int: Hash value
        """
        return hash(self.name.lower())

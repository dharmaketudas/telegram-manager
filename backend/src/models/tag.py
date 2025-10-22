"""
Tag domain model.

This module defines the Tag dataclass that represents tags for organizing
contacts in the Telegram Contact Manager application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Tag:
    """
    Represents a tag for organizing contacts.

    Tags can be assigned to contacts to categorize and filter them.
    Each tag can have a color for visual distinction.

    Attributes:
        id: Internal database ID (None for new tags)
        name: Unique tag name
        color: Hex color code for visual representation (e.g., "#FF5733")
        created_at: Timestamp when tag was created
    """

    id: Optional[int]
    name: str
    color: Optional[str]
    created_at: datetime

    def __str__(self) -> str:
        """String representation of the tag."""
        color_str = f" ({self.color})" if self.color else ""
        return f"Tag({self.name}{color_str})"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
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

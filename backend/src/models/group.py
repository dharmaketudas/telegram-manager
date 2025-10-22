"""
Group domain model.

This module defines the Group dataclass that represents Telegram group/chat
entities in the Telegram Contact Manager application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Group:
    """
    Represents a Telegram group or supergroup.

    Attributes:
        id: Internal database ID (None for new groups)
        telegram_id: Unique Telegram group/chat ID
        name: Group name
        member_count: Number of members in the group
        profile_photo_path: Path to stored group profile photo
        created_at: Timestamp when group was first discovered
        updated_at: Timestamp when group was last updated
    """

    id: Optional[int]
    telegram_id: int
    name: str
    member_count: int
    profile_photo_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    def __str__(self) -> str:
        """String representation of the group."""
        return f"Group({self.name}, {self.member_count} members)"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (
            f"Group(id={self.id}, telegram_id={self.telegram_id}, "
            f"name={self.name}, member_count={self.member_count})"
        )

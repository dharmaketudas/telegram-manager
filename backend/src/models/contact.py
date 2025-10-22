"""
Contact domain model.

This module defines the Contact and ContactProfile dataclasses that represent
contact entities in the Telegram Contact Manager application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Contact:
    """
    Represents a Telegram contact.

    Attributes:
        id: Internal database ID (None for new contacts)
        telegram_id: Unique Telegram user ID
        username: Telegram username (without @)
        first_name: Contact's first name
        last_name: Contact's last name
        display_name: Preferred display name
        phone: Phone number (if available)
        profile_photo_path: Path to stored profile photo
        bio: User's bio/about text
        created_at: Timestamp when contact was first discovered
        updated_at: Timestamp when contact was last updated
    """

    id: Optional[int]
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: str
    phone: Optional[str]
    profile_photo_path: Optional[str]
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        """
        Generates a full name for the contact.

        Returns the concatenation of first_name and last_name if available,
        otherwise falls back to username, or a generic identifier using
        the telegram_id.

        Returns:
            str: The full name or fallback identifier
        """
        parts = [self.first_name, self.last_name]
        name = " ".join(filter(None, parts))

        if name:
            return name
        elif self.username:
            return self.username
        else:
            return f"User {self.telegram_id}"

    def __str__(self) -> str:
        """String representation of the contact."""
        return f"Contact({self.full_name}, @{self.username or 'no_username'})"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (
            f"Contact(id={self.id}, telegram_id={self.telegram_id}, "
            f"username={self.username}, full_name={self.full_name})"
        )


@dataclass
class ContactProfile:
    """
    Aggregated view of a contact with related data.

    This dataclass combines a contact with their tags, mutual groups,
    and recent message history to provide a complete profile view.

    Attributes:
        contact: The Contact object
        tags: List of tags assigned to this contact
        mutual_groups: List of groups where both user and contact are members
        last_received_message: Most recent message received from this contact
        last_sent_message: Most recent message sent to this contact
    """

    contact: Contact
    tags: List["Tag"]  # Forward reference to avoid circular import
    mutual_groups: List["Group"]  # Forward reference to avoid circular import
    last_received_message: Optional["Message"]  # Forward reference
    last_sent_message: Optional["Message"]  # Forward reference

    def __str__(self) -> str:
        """String representation of the contact profile."""
        tag_count = len(self.tags)
        group_count = len(self.mutual_groups)
        return (
            f"ContactProfile({self.contact.full_name}, "
            f"{tag_count} tags, {group_count} mutual groups)"
        )


# Type hints for forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tag import Tag
    from .group import Group
    from .message import Message

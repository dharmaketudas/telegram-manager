"""
Message domain model.

This module defines the Message dataclass that represents messages exchanged
with contacts in the Telegram Contact Manager application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    """
    Represents a message exchanged with a contact.

    This model tracks messages sent to and received from contacts,
    storing essential information for displaying conversation history.

    Attributes:
        id: Internal database ID (None for new messages)
        telegram_message_id: Telegram's unique message ID
        contact_id: ID of the contact this message is associated with
        is_outgoing: True if message was sent by user, False if received
        content: Text content of the message
        timestamp: When the message was sent/received
        created_at: When this record was created in our database
    """

    id: Optional[int]
    telegram_message_id: Optional[int]
    contact_id: int
    is_outgoing: bool
    content: Optional[str]
    timestamp: datetime
    created_at: datetime

    @property
    def direction(self) -> str:
        """
        Returns a human-readable direction indicator.

        Returns:
            str: "sent" if outgoing, "received" if incoming
        """
        return "sent" if self.is_outgoing else "received"

    @property
    def preview(self) -> str:
        """
        Returns a preview of the message content.

        Truncates long messages to 100 characters and adds ellipsis.

        Returns:
            str: Message preview or "[No content]" if empty
        """
        if not self.content:
            return "[No content]"

        max_length = 100
        if len(self.content) <= max_length:
            return self.content

        return self.content[:max_length] + "..."

    def __str__(self) -> str:
        """String representation of the message."""
        direction = "→" if self.is_outgoing else "←"
        return f"Message({direction} {self.preview})"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (
            f"Message(id={self.id}, telegram_message_id={self.telegram_message_id}, "
            f"contact_id={self.contact_id}, is_outgoing={self.is_outgoing}, "
            f"timestamp={self.timestamp})"
        )

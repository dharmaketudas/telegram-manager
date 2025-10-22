"""
Domain models for the Telegram Contact Manager.

This package contains dataclass models that represent the core domain entities
of the application. These models are used throughout the application for
data transfer and business logic.
"""

from .contact import Contact, ContactProfile
from .group import Group
from .tag import Tag
from .message import Message

__all__ = [
    "Contact",
    "ContactProfile",
    "Group",
    "Tag",
    "Message",
]

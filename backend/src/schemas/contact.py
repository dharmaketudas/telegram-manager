"""
Contact-related Pydantic schemas for API requests and responses.

This module defines the schemas for contact-related API endpoints,
including contact lists, profiles, groups, and messages.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class GroupInfo(BaseModel):
    """
    Schema for group information in contact profiles.

    Represents a Telegram group where both the user and contact are members.
    """

    id: int = Field(..., description="Internal database ID of the group", examples=[1])
    telegram_id: int = Field(
        ..., description="Telegram's unique group ID", examples=[1001234567890]
    )
    name: str = Field(
        ...,
        description="Group name",
        examples=["Python Developers", "Tech Enthusiasts"],
    )
    member_count: int = Field(
        ..., description="Number of members in the group", examples=[150, 1000]
    )
    profile_photo_url: Optional[str] = Field(
        None,
        description="URL to the group's profile photo",
        examples=["/api/media/group-photos/1001234567890.jpg"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "telegram_id": 1001234567890,
                "name": "Python Developers",
                "member_count": 150,
                "profile_photo_url": "/api/media/group-photos/1001234567890.jpg",
            }
        }
    )


class MessageInfo(BaseModel):
    """
    Schema for message information in contact profiles.

    Represents a sent or received message with a contact.
    """

    id: int = Field(
        ..., description="Internal database ID of the message", examples=[1]
    )
    content: Optional[str] = Field(
        None,
        description="Text content of the message (None for media-only messages)",
        examples=["Hello, how are you?", "Thanks for your help!"],
    )
    timestamp: datetime = Field(
        ...,
        description="When the message was sent/received",
        examples=["2024-01-01T12:00:00"],
    )
    is_outgoing: bool = Field(
        ...,
        description="True if message was sent by user, False if received",
        examples=[True, False],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "content": "Hello, how are you?",
                "timestamp": "2024-01-01T12:00:00",
                "is_outgoing": True,
            }
        }
    )


class ContactResponse(BaseModel):
    """
    Schema for contact information in list responses.

    Used when returning lists of contacts or individual contact details.
    """

    id: int = Field(
        ..., description="Internal database ID of the contact", examples=[1]
    )
    telegram_id: int = Field(
        ..., description="Telegram's unique user ID", examples=[123456789]
    )
    username: Optional[str] = Field(
        None,
        description="Telegram username (without @)",
        examples=["john_doe", "alice_smith"],
    )
    first_name: Optional[str] = Field(
        None, description="Contact's first name", examples=["John", "Alice"]
    )
    last_name: Optional[str] = Field(
        None, description="Contact's last name", examples=["Doe", "Smith"]
    )
    display_name: str = Field(
        ...,
        description="Preferred display name for the contact",
        examples=["John Doe", "Alice Smith"],
    )
    phone: Optional[str] = Field(
        None,
        description="Phone number if available",
        examples=["+1234567890", "+447123456789"],
    )
    profile_photo_url: Optional[str] = Field(
        None,
        description="URL to the contact's profile photo",
        examples=["/api/media/profile-photos/123456789.jpg"],
    )
    tags: List[str] = Field(
        default_factory=list,
        description="List of tag names assigned to this contact",
        examples=[["Work", "Friend"], ["Family"], []],
    )
    updated_at: datetime = Field(
        ...,
        description="When the contact was last updated",
        examples=["2024-01-01T12:00:00"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "telegram_id": 123456789,
                "username": "john_doe",
                "first_name": "John",
                "last_name": "Doe",
                "display_name": "John Doe",
                "phone": "+1234567890",
                "profile_photo_url": "/api/media/profile-photos/123456789.jpg",
                "tags": ["Work", "Friend"],
                "updated_at": "2024-01-01T12:00:00",
            }
        },
    )


class ContactProfileResponse(BaseModel):
    """
    Schema for detailed contact profile responses.

    Includes the contact information along with tags, mutual groups,
    and recent message history.
    """

    contact: ContactResponse = Field(..., description="The contact's basic information")
    tags: List["TagResponse"] = Field(
        default_factory=list,
        description="Tags assigned to this contact with full details",
    )
    mutual_groups: List[GroupInfo] = Field(
        default_factory=list,
        description="Groups where both user and contact are members",
    )
    last_received_message: Optional[MessageInfo] = Field(
        None, description="Most recent message received from this contact"
    )
    last_sent_message: Optional[MessageInfo] = Field(
        None, description="Most recent message sent to this contact"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "contact": {
                    "id": 1,
                    "telegram_id": 123456789,
                    "username": "john_doe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "display_name": "John Doe",
                    "phone": "+1234567890",
                    "profile_photo_url": "/api/media/profile-photos/123456789.jpg",
                    "tags": ["Work", "Friend"],
                    "updated_at": "2024-01-01T12:00:00",
                },
                "tags": [
                    {
                        "id": 1,
                        "name": "Work",
                        "color": "#FF5733",
                        "created_at": "2024-01-01T10:00:00",
                        "contact_count": 25,
                    }
                ],
                "mutual_groups": [
                    {
                        "id": 1,
                        "telegram_id": 1001234567890,
                        "name": "Python Developers",
                        "member_count": 150,
                        "profile_photo_url": "/api/media/group-photos/1001234567890.jpg",
                    }
                ],
                "last_received_message": {
                    "id": 1,
                    "content": "Hey there!",
                    "timestamp": "2024-01-01T11:30:00",
                    "is_outgoing": False,
                },
                "last_sent_message": {
                    "id": 2,
                    "content": "Hi! How are you?",
                    "timestamp": "2024-01-01T11:35:00",
                    "is_outgoing": True,
                },
            }
        }
    )


# Forward reference resolution
from .tag import TagResponse

ContactProfileResponse.model_rebuild()

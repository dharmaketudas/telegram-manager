"""
Message-related Pydantic schemas for API requests and responses.

This module defines the schemas for message-related API endpoints,
including sending single messages, bulk messaging, and tracking message status.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class SendMessageRequest(BaseModel):
    """
    Schema for sending a message to a single contact.

    Used when the user wants to send a direct message to one contact.
    """

    contact_id: int = Field(
        ...,
        gt=0,
        description="ID of the contact to send the message to",
        examples=[1, 5, 42],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="Message text to send (1-4096 characters, Telegram limit)",
        examples=[
            "Hello, how are you?",
            "Thanks for your help!",
            "Let's meet tomorrow at 3 PM.",
        ],
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message - trim whitespace and ensure not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty or only whitespace")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "contact_id": 1,
                "message": "Hello, how are you?",
            }
        }
    )


class BulkMessageRequest(BaseModel):
    """
    Schema for sending a message to multiple contacts by tag.

    Used when the user wants to send the same message to all contacts
    with specific tags.
    """

    tag_ids: List[int] = Field(
        ...,
        min_length=1,
        description="List of tag IDs - contacts with ANY of these tags will receive the message",
        examples=[[1], [1, 2], [1, 2, 3]],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="Message text to send to all matching contacts (1-4096 characters)",
        examples=[
            "Hello everyone!",
            "Important announcement: Meeting tomorrow at 10 AM.",
        ],
    )

    @field_validator("tag_ids")
    @classmethod
    def validate_tag_ids(cls, v: List[int]) -> List[int]:
        """Validate tag IDs are positive and unique."""
        if not v:
            raise ValueError("At least one tag ID must be provided")

        for tag_id in v:
            if tag_id <= 0:
                raise ValueError("Tag IDs must be positive integers")

        # Remove duplicates while preserving order
        seen = set()
        unique_ids = []
        for tag_id in v:
            if tag_id not in seen:
                seen.add(tag_id)
                unique_ids.append(tag_id)

        return unique_ids

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message - trim whitespace and ensure not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty or only whitespace")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tag_ids": [1, 2],
                "message": "Hello everyone! Hope you're having a great day.",
            }
        }
    )


class MessageResult(BaseModel):
    """
    Schema for the result of sending a message to a single contact.

    Used to track success/failure for each message in bulk operations.
    """

    contact_id: int = Field(
        ...,
        description="ID of the contact this result is for",
        examples=[1, 5, 42],
    )
    contact_name: str = Field(
        ...,
        description="Name of the contact for easy identification",
        examples=["John Doe", "Alice Smith"],
    )
    success: bool = Field(
        ...,
        description="Whether the message was sent successfully",
        examples=[True, False],
    )
    message_id: Optional[int] = Field(
        None,
        description="Telegram message ID if successful",
        examples=[12345, 67890, None],
    )
    error: Optional[str] = Field(
        None,
        description="Error message if sending failed",
        examples=[
            None,
            "User has blocked the bot",
            "Network timeout",
            "Rate limit exceeded",
        ],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "contact_id": 1,
                "contact_name": "John Doe",
                "success": True,
                "message_id": 12345,
                "error": None,
            }
        }
    )


class BulkMessageJob(BaseModel):
    """
    Schema for the initial response when starting a bulk message job.

    Returned immediately when a bulk message request is initiated.
    """

    job_id: str = Field(
        ...,
        description="Unique identifier for this bulk message job",
        examples=[
            "bulk_msg_20240101_120000_abc123",
            "bulk_msg_20240115_143022_def456",
        ],
    )
    total_contacts: int = Field(
        ...,
        ge=0,
        description="Total number of contacts that will receive the message",
        examples=[5, 25, 100],
    )
    status: str = Field(
        ...,
        description="Current status of the job",
        examples=["pending", "in_progress", "completed", "failed"],
    )
    started_at: datetime = Field(
        ...,
        description="When the job was started",
        examples=["2024-01-01T12:00:00"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "bulk_msg_20240101_120000_abc123",
                "total_contacts": 25,
                "status": "pending",
                "started_at": "2024-01-01T12:00:00",
            }
        }
    )


class BulkMessageStatus(BaseModel):
    """
    Schema for the status of an ongoing or completed bulk message job.

    Used to track progress and results of bulk messaging operations.
    """

    job_id: str = Field(
        ...,
        description="Unique identifier for this bulk message job",
        examples=["bulk_msg_20240101_120000_abc123"],
    )
    total_contacts: int = Field(
        ...,
        ge=0,
        description="Total number of contacts in this job",
        examples=[25, 100],
    )
    sent: int = Field(
        ...,
        ge=0,
        description="Number of messages successfully sent",
        examples=[20, 95],
    )
    failed: int = Field(
        ...,
        ge=0,
        description="Number of messages that failed to send",
        examples=[0, 5],
    )
    in_progress: bool = Field(
        ...,
        description="Whether the job is still in progress",
        examples=[True, False],
    )
    status: str = Field(
        ...,
        description="Current status of the job",
        examples=["pending", "in_progress", "completed", "failed"],
    )
    started_at: datetime = Field(
        ...,
        description="When the job was started",
        examples=["2024-01-01T12:00:00"],
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="When the job was completed (if finished)",
        examples=["2024-01-01T12:05:00", None],
    )
    failures: List[MessageResult] = Field(
        default_factory=list,
        description="List of failed message results with error details",
    )
    message: Optional[str] = Field(
        None,
        description="The message text that was sent",
        examples=["Hello everyone!", None],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "bulk_msg_20240101_120000_abc123",
                "total_contacts": 25,
                "sent": 23,
                "failed": 2,
                "in_progress": False,
                "status": "completed",
                "started_at": "2024-01-01T12:00:00",
                "completed_at": "2024-01-01T12:05:00",
                "failures": [
                    {
                        "contact_id": 5,
                        "contact_name": "Jane Doe",
                        "success": False,
                        "message_id": None,
                        "error": "User has blocked the bot",
                    }
                ],
                "message": "Hello everyone!",
            }
        }
    )

"""
Tag-related Pydantic schemas for API requests and responses.

This module defines the schemas for tag-related API endpoints,
including tag creation, updates, and responses.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re


class TagCreate(BaseModel):
    """
    Schema for creating a new tag.

    Used when a user wants to create a tag to organize contacts.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Name of the tag (1-50 characters)",
        examples=["Work", "Family", "Friends", "Important"],
    )
    color: Optional[str] = Field(
        None,
        description="Hex color code for the tag (e.g., #FF5733)",
        examples=["#FF5733", "#00FF00", "#3498DB", None],
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate tag name - trim whitespace and ensure not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Tag name cannot be empty or only whitespace")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color is a valid hex color code."""
        if v is None:
            return v

        v = v.strip()
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be a valid hex color code (e.g., #FF5733)")
        return v.upper()  # Normalize to uppercase

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Work",
                "color": "#FF5733",
            }
        }
    )


class TagUpdate(BaseModel):
    """
    Schema for updating an existing tag.

    All fields are optional - only provided fields will be updated.
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="New name for the tag (1-50 characters)",
        examples=["Work", "Family", "Friends"],
    )
    color: Optional[str] = Field(
        None,
        description="New hex color code for the tag",
        examples=["#FF5733", "#00FF00", "#3498DB"],
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate tag name - trim whitespace and ensure not empty."""
        if v is None:
            return v

        v = v.strip()
        if not v:
            raise ValueError("Tag name cannot be empty or only whitespace")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color is a valid hex color code."""
        if v is None:
            return v

        v = v.strip()
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be a valid hex color code (e.g., #FF5733)")
        return v.upper()  # Normalize to uppercase

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Work Projects",
                "color": "#3498DB",
            }
        }
    )


class TagResponse(BaseModel):
    """
    Schema for tag information in responses.

    Includes the tag details and the number of contacts assigned to it.
    """

    id: int = Field(..., description="Internal database ID of the tag", examples=[1])
    name: str = Field(
        ...,
        description="Name of the tag",
        examples=["Work", "Family", "Friends", "Important"],
    )
    color: Optional[str] = Field(
        None,
        description="Hex color code for the tag",
        examples=["#FF5733", "#00FF00", "#3498DB", None],
    )
    created_at: datetime = Field(
        ...,
        description="When the tag was created",
        examples=["2024-01-01T10:00:00"],
    )
    contact_count: int = Field(
        0,
        description="Number of contacts assigned to this tag",
        examples=[0, 5, 25, 100],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Work",
                "color": "#FF5733",
                "created_at": "2024-01-01T10:00:00",
                "contact_count": 25,
            }
        },
    )

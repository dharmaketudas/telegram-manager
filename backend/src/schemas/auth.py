"""
Authentication-related Pydantic schemas for API requests and responses.

This module defines the schemas for authentication-related API endpoints,
including login flow, code verification, and session management.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
import re


class AuthInitRequest(BaseModel):
    """
    Schema for initiating the authentication process.

    Used when a user provides their Telegram API credentials to start
    the authentication flow.
    """

    api_id: int = Field(
        ...,
        gt=0,
        description="Telegram API ID (get from https://my.telegram.org)",
        examples=[12345, 67890],
    )
    api_hash: str = Field(
        ...,
        min_length=32,
        max_length=32,
        description="Telegram API Hash (32 characters)",
        examples=["abcdef1234567890abcdef1234567890"],
    )
    phone: str = Field(
        ...,
        description="Phone number in international format (with country code)",
        examples=["+1234567890", "+447123456789", "+919876543210"],
    )

    @field_validator("api_hash")
    @classmethod
    def validate_api_hash(cls, v: str) -> str:
        """Validate API hash format."""
        v = v.strip()
        if not re.match(r"^[a-fA-F0-9]{32}$", v):
            raise ValueError("API hash must be a 32-character hexadecimal string")
        return v.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        v = v.strip()
        # Remove spaces and dashes for validation
        clean_phone = v.replace(" ", "").replace("-", "")

        if not clean_phone.startswith("+"):
            raise ValueError("Phone number must start with + and country code")

        if not re.match(r"^\+[1-9]\d{1,14}$", clean_phone):
            raise ValueError(
                "Invalid phone number format. Use international format: +[country code][number]"
            )

        return clean_phone

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api_id": 12345,
                "api_hash": "abcdef1234567890abcdef1234567890",
                "phone": "+1234567890",
            }
        }
    )


class AuthCodeRequest(BaseModel):
    """
    Schema for submitting the verification code.

    Used when the user receives a verification code via Telegram
    and needs to submit it to complete authentication.
    """

    phone: str = Field(
        ...,
        description="Phone number that received the code",
        examples=["+1234567890", "+447123456789"],
    )
    code: str = Field(
        ...,
        min_length=5,
        max_length=6,
        description="Verification code received via Telegram (5-6 digits)",
        examples=["12345", "123456"],
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        v = v.strip()
        clean_phone = v.replace(" ", "").replace("-", "")

        if not clean_phone.startswith("+"):
            raise ValueError("Phone number must start with + and country code")

        if not re.match(r"^\+[1-9]\d{1,14}$", clean_phone):
            raise ValueError("Invalid phone number format")

        return clean_phone

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate verification code format."""
        v = v.strip()
        if not re.match(r"^\d{5,6}$", v):
            raise ValueError("Verification code must be 5-6 digits")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phone": "+1234567890",
                "code": "12345",
            }
        }
    )


class AuthPasswordRequest(BaseModel):
    """
    Schema for submitting the 2FA password.

    Used when the user has two-factor authentication enabled
    and needs to provide their password.
    """

    password: str = Field(
        ...,
        min_length=1,
        description="Two-factor authentication password",
        examples=["MySecurePassword123"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password is not empty."""
        if not v.strip():
            raise ValueError("Password cannot be empty or only whitespace")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "password": "MySecurePassword123",
            }
        }
    )


class AuthResponse(BaseModel):
    """
    Schema for authentication responses.

    Returned after any authentication operation to indicate the
    current state and what action is needed next.
    """

    success: bool = Field(
        ...,
        description="Whether the authentication step was successful",
        examples=[True, False],
    )
    requires_code: bool = Field(
        False,
        description="Whether a verification code needs to be submitted",
        examples=[True, False],
    )
    requires_password: bool = Field(
        False,
        description="Whether a 2FA password needs to be submitted",
        examples=[True, False],
    )
    message: str = Field(
        ...,
        description="Human-readable message describing the result or next step",
        examples=[
            "Authentication successful",
            "Verification code sent to your Telegram app",
            "Please enter your 2FA password",
            "Invalid verification code",
            "Authentication failed",
        ],
    )
    phone: Optional[str] = Field(
        None,
        description="Phone number associated with the session",
        examples=["+1234567890", None],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "requires_code": True,
                "requires_password": False,
                "message": "Verification code sent to your Telegram app",
                "phone": "+1234567890",
            }
        }
    )


class AuthStatusResponse(BaseModel):
    """
    Schema for checking authentication status.

    Used to check if the user is currently authenticated and
    their session is valid.
    """

    authenticated: bool = Field(
        ...,
        description="Whether the user is currently authenticated",
        examples=[True, False],
    )
    phone: Optional[str] = Field(
        None,
        description="Phone number of the authenticated session",
        examples=["+1234567890", None],
    )
    session_valid: bool = Field(
        ...,
        description="Whether the current session is valid and active",
        examples=[True, False],
    )
    user_id: Optional[int] = Field(
        None,
        description="Telegram user ID of the authenticated user",
        examples=[123456789, None],
    )
    username: Optional[str] = Field(
        None,
        description="Username of the authenticated user",
        examples=["john_doe", None],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "authenticated": True,
                "phone": "+1234567890",
                "session_valid": True,
                "user_id": 123456789,
                "username": "john_doe",
            }
        }
    )

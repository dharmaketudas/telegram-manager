"""
API Schemas for the Telegram Contact Manager.

This package contains Pydantic models that define the API contracts
between the backend and frontend. These schemas handle:
- Request validation
- Response serialization
- API documentation
- Type safety
"""

from .contact import (
    ContactResponse,
    ContactProfileResponse,
    GroupInfo,
    MessageInfo,
)
from .tag import (
    TagCreate,
    TagUpdate,
    TagResponse,
)
from .message import (
    SendMessageRequest,
    BulkMessageRequest,
    MessageResult,
    BulkMessageJob,
    BulkMessageStatus,
)
from .auth import (
    AuthInitRequest,
    AuthCodeRequest,
    AuthPasswordRequest,
    AuthResponse,
    AuthStatusResponse,
)

__all__ = [
    # Contact schemas
    "ContactResponse",
    "ContactProfileResponse",
    "GroupInfo",
    "MessageInfo",
    # Tag schemas
    "TagCreate",
    "TagUpdate",
    "TagResponse",
    # Message schemas
    "SendMessageRequest",
    "BulkMessageRequest",
    "MessageResult",
    "BulkMessageJob",
    "BulkMessageStatus",
    # Auth schemas
    "AuthInitRequest",
    "AuthCodeRequest",
    "AuthPasswordRequest",
    "AuthResponse",
    "AuthStatusResponse",
]

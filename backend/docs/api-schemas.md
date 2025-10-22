# API Schemas Documentation

**Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** Complete ✅

---

## 📖 Overview

This document provides comprehensive documentation for all Pydantic schemas used in the Telegram Contact Manager API. These schemas define the contracts between the backend and frontend, handling request validation, response serialization, and API documentation.

### Purpose

API schemas serve as:
- **Request Validators** - Ensure incoming data meets requirements
- **Response Serializers** - Format outgoing data consistently
- **API Documentation** - Auto-generate OpenAPI/Swagger docs
- **Type Safety** - Provide type hints for IDE support

### Location

All API schemas are located in the `src/schemas/` directory:

```
src/schemas/
├── __init__.py        # Package exports
├── contact.py         # Contact-related schemas
├── tag.py             # Tag-related schemas
├── message.py         # Message-related schemas
└── auth.py            # Authentication schemas
```

---

## 🏗️ Architecture

### Design Principles

1. **Validation First** - All input is validated before processing
2. **Clear Error Messages** - Validation errors are descriptive
3. **Type Safety** - All fields have explicit type hints
4. **Examples Included** - Each schema has example values
5. **Consistent Naming** - Follow clear naming conventions

### Schema Types

- **Request Schemas** - Used for incoming API requests (e.g., `TagCreate`, `SendMessageRequest`)
- **Response Schemas** - Used for outgoing API responses (e.g., `ContactResponse`, `TagResponse`)
- **Info Schemas** - Nested data structures (e.g., `GroupInfo`, `MessageInfo`)

### Import Pattern

```python
# Import all schemas from the package
from src.schemas import (
    ContactResponse,
    TagCreate,
    SendMessageRequest,
    AuthInitRequest,
)

# Or import from specific modules
from src.schemas.contact import ContactResponse
from src.schemas.tag import TagCreate
```

---

## 📦 Contact Schemas

### GroupInfo

Information about a Telegram group.

**Usage:** Nested in `ContactProfileResponse` to show mutual groups.

```python
class GroupInfo(BaseModel):
    id: int
    telegram_id: int
    name: str
    member_count: int
    profile_photo_url: Optional[str]
```

**Example:**

```json
{
  "id": 1,
  "telegram_id": 1001234567890,
  "name": "Python Developers",
  "member_count": 150,
  "profile_photo_url": "/api/media/group-photos/1001234567890.jpg"
}
```

---

### MessageInfo

Information about a sent or received message.

**Usage:** Nested in `ContactProfileResponse` for message history.

```python
class MessageInfo(BaseModel):
    id: int
    content: Optional[str]
    timestamp: datetime
    is_outgoing: bool
```

**Field Details:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Internal database ID |
| `content` | `Optional[str]` | Message text (None for media-only) |
| `timestamp` | `datetime` | When message was sent/received |
| `is_outgoing` | `bool` | True if sent by user, False if received |

**Example:**

```json
{
  "id": 1,
  "content": "Hello, how are you?",
  "timestamp": "2024-01-01T12:00:00",
  "is_outgoing": true
}
```

---

### ContactResponse

Basic contact information for list views.

**Usage:** Returned by `GET /api/contacts` and contact detail endpoints.

```python
class ContactResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: str
    phone: Optional[str]
    profile_photo_url: Optional[str]
    tags: List[str]
    updated_at: datetime
```

**Example:**

```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "display_name": "John Doe",
  "phone": "+1234567890",
  "profile_photo_url": "/api/media/profile-photos/123456789.jpg",
  "tags": ["Work", "Friend"],
  "updated_at": "2024-01-01T12:00:00"
}
```

---

### ContactProfileResponse

Detailed contact profile with related data.

**Usage:** Returned by `GET /api/contacts/{id}/profile` for full profile view.

```python
class ContactProfileResponse(BaseModel):
    contact: ContactResponse
    tags: List[TagResponse]
    mutual_groups: List[GroupInfo]
    last_received_message: Optional[MessageInfo]
    last_sent_message: Optional[MessageInfo]
```

**Example:**

```json
{
  "contact": {
    "id": 1,
    "telegram_id": 123456789,
    "username": "john_doe",
    "display_name": "John Doe",
    "tags": ["Work"],
    "updated_at": "2024-01-01T12:00:00"
  },
  "tags": [
    {
      "id": 1,
      "name": "Work",
      "color": "#FF5733",
      "created_at": "2024-01-01T10:00:00",
      "contact_count": 25
    }
  ],
  "mutual_groups": [
    {
      "id": 1,
      "telegram_id": 1001234567890,
      "name": "Python Developers",
      "member_count": 150,
      "profile_photo_url": "/api/media/group-photos/1001234567890.jpg"
    }
  ],
  "last_received_message": {
    "id": 1,
    "content": "Hey there!",
    "timestamp": "2024-01-01T11:30:00",
    "is_outgoing": false
  },
  "last_sent_message": {
    "id": 2,
    "content": "Hi! How are you?",
    "timestamp": "2024-01-01T11:35:00",
    "is_outgoing": true
  }
}
```

---

## 🏷️ Tag Schemas

### TagCreate

Request schema for creating a new tag.

**Usage:** Used with `POST /api/tags`.

```python
class TagCreate(BaseModel):
    name: str  # 1-50 characters, trimmed
    color: Optional[str]  # Hex color code (e.g., #FF5733)
```

**Validation Rules:**

- `name`: 1-50 characters, whitespace trimmed, cannot be empty
- `color`: Must be valid hex color code (6 hex digits with #), normalized to uppercase

**Example Request:**

```json
{
  "name": "Work",
  "color": "#FF5733"
}
```

**Validation Examples:**

```python
# ✅ Valid
TagCreate(name="Work", color="#FF5733")
TagCreate(name="Personal", color=None)
TagCreate(name="  Work  ", color="#ff5733")  # Trimmed and normalized

# ❌ Invalid
TagCreate(name="", color=None)  # Empty name
TagCreate(name="   ", color=None)  # Whitespace only
TagCreate(name="Work", color="FF5733")  # Missing #
TagCreate(name="Work", color="#GG5733")  # Invalid hex
TagCreate(name="A" * 51, color=None)  # Too long
```

---

### TagUpdate

Request schema for updating an existing tag.

**Usage:** Used with `PUT /api/tags/{id}`.

```python
class TagUpdate(BaseModel):
    name: Optional[str]  # 1-50 characters, trimmed
    color: Optional[str]  # Hex color code
```

**Note:** All fields are optional. Only provided fields will be updated.

**Example Request:**

```json
{
  "name": "Work Projects",
  "color": "#3498DB"
}
```

**Or update only one field:**

```json
{
  "color": "#3498DB"
}
```

---

### TagResponse

Response schema for tag information.

**Usage:** Returned by tag endpoints and nested in contact profiles.

```python
class TagResponse(BaseModel):
    id: int
    name: str
    color: Optional[str]
    created_at: datetime
    contact_count: int
```

**Example:**

```json
{
  "id": 1,
  "name": "Work",
  "color": "#FF5733",
  "created_at": "2024-01-01T10:00:00",
  "contact_count": 25
}
```

---

## 💬 Message Schemas

### SendMessageRequest

Request schema for sending a message to a single contact.

**Usage:** Used with `POST /api/messages/send`.

```python
class SendMessageRequest(BaseModel):
    contact_id: int  # Must be > 0
    message: str  # 1-4096 characters, trimmed
```

**Validation Rules:**

- `contact_id`: Must be positive integer
- `message`: 1-4096 characters (Telegram limit), whitespace trimmed, cannot be empty

**Example Request:**

```json
{
  "contact_id": 1,
  "message": "Hello, how are you?"
}
```

---

### BulkMessageRequest

Request schema for sending messages to multiple contacts by tag.

**Usage:** Used with `POST /api/messages/bulk`.

```python
class BulkMessageRequest(BaseModel):
    tag_ids: List[int]  # At least 1, all positive
    message: str  # 1-4096 characters, trimmed
```

**Validation Rules:**

- `tag_ids`: At least one tag ID, all must be positive, duplicates removed
- `message`: 1-4096 characters, whitespace trimmed, cannot be empty

**Example Request:**

```json
{
  "tag_ids": [1, 2, 3],
  "message": "Hello everyone! Hope you're having a great day."
}
```

**Deduplication Example:**

```python
# Input
BulkMessageRequest(tag_ids=[1, 2, 1, 3, 2], message="Hello")

# After validation
# tag_ids = [1, 2, 3]  (duplicates removed, order preserved)
```

---

### MessageResult

Result of sending a message to a single contact.

**Usage:** Nested in `BulkMessageStatus` for tracking individual results.

```python
class MessageResult(BaseModel):
    contact_id: int
    contact_name: str
    success: bool
    message_id: Optional[int]
    error: Optional[str]
```

**Example (Success):**

```json
{
  "contact_id": 1,
  "contact_name": "John Doe",
  "success": true,
  "message_id": 12345,
  "error": null
}
```

**Example (Failure):**

```json
{
  "contact_id": 5,
  "contact_name": "Jane Doe",
  "success": false,
  "message_id": null,
  "error": "User has blocked the bot"
}
```

---

### BulkMessageJob

Initial response when starting a bulk message job.

**Usage:** Returned immediately by `POST /api/messages/bulk`.

```python
class BulkMessageJob(BaseModel):
    job_id: str
    total_contacts: int
    status: str  # "pending", "in_progress", "completed", "failed"
    started_at: datetime
```

**Example:**

```json
{
  "job_id": "bulk_msg_20240101_120000_abc123",
  "total_contacts": 25,
  "status": "pending",
  "started_at": "2024-01-01T12:00:00"
}
```

---

### BulkMessageStatus

Status and results of a bulk message job.

**Usage:** Returned by `GET /api/messages/status/{job_id}`.

```python
class BulkMessageStatus(BaseModel):
    job_id: str
    total_contacts: int
    sent: int
    failed: int
    in_progress: bool
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    failures: List[MessageResult]
    message: Optional[str]
```

**Example (In Progress):**

```json
{
  "job_id": "bulk_msg_20240101_120000_abc123",
  "total_contacts": 25,
  "sent": 10,
  "failed": 0,
  "in_progress": true,
  "status": "in_progress",
  "started_at": "2024-01-01T12:00:00",
  "completed_at": null,
  "failures": [],
  "message": "Hello everyone!"
}
```

**Example (Completed):**

```json
{
  "job_id": "bulk_msg_20240101_120000_abc123",
  "total_contacts": 25,
  "sent": 23,
  "failed": 2,
  "in_progress": false,
  "status": "completed",
  "started_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:05:00",
  "failures": [
    {
      "contact_id": 5,
      "contact_name": "Jane Doe",
      "success": false,
      "message_id": null,
      "error": "User has blocked the bot"
    }
  ],
  "message": "Hello everyone!"
}
```

---

## 🔐 Authentication Schemas

### AuthInitRequest

Request schema for initiating authentication.

**Usage:** Used with `POST /api/auth/init`.

```python
class AuthInitRequest(BaseModel):
    api_id: int  # Must be > 0
    api_hash: str  # 32-character hex string
    phone: str  # International format with +
```

**Validation Rules:**

- `api_id`: Must be positive integer
- `api_hash`: Must be exactly 32 hexadecimal characters, normalized to lowercase
- `phone`: Must start with +, follow international format, spaces/dashes removed

**Example Request:**

```json
{
  "api_id": 12345,
  "api_hash": "abcdef1234567890abcdef1234567890",
  "phone": "+1234567890"
}
```

**Phone Format Examples:**

```python
# ✅ Valid
"+1234567890"
"+447123456789"
"+919876543210"
"+1 234 567 890"  # Spaces removed during validation

# ❌ Invalid
"1234567890"  # Missing +
"+0123456789"  # Can't start with 0 after +
```

---

### AuthCodeRequest

Request schema for submitting verification code.

**Usage:** Used with `POST /api/auth/code`.

```python
class AuthCodeRequest(BaseModel):
    phone: str  # International format with +
    code: str  # 5-6 digits
```

**Validation Rules:**

- `phone`: Same validation as `AuthInitRequest`
- `code`: Must be 5 or 6 digits, numeric only

**Example Request:**

```json
{
  "phone": "+1234567890",
  "code": "12345"
}
```

---

### AuthPasswordRequest

Request schema for submitting 2FA password.

**Usage:** Used with `POST /api/auth/password`.

```python
class AuthPasswordRequest(BaseModel):
    password: str  # At least 1 character
```

**Validation Rules:**

- `password`: Cannot be empty or only whitespace

**Example Request:**

```json
{
  "password": "MySecurePassword123"
}
```

---

### AuthResponse

Response schema for authentication operations.

**Usage:** Returned by all authentication endpoints.

```python
class AuthResponse(BaseModel):
    success: bool
    requires_code: bool
    requires_password: bool
    message: str
    phone: Optional[str]
```

**Example (Code Required):**

```json
{
  "success": true,
  "requires_code": true,
  "requires_password": false,
  "message": "Verification code sent to your Telegram app",
  "phone": "+1234567890"
}
```

**Example (Password Required):**

```json
{
  "success": true,
  "requires_code": false,
  "requires_password": true,
  "message": "Please enter your 2FA password",
  "phone": "+1234567890"
}
```

**Example (Success):**

```json
{
  "success": true,
  "requires_code": false,
  "requires_password": false,
  "message": "Authentication successful",
  "phone": "+1234567890"
}
```

---

### AuthStatusResponse

Response schema for checking authentication status.

**Usage:** Returned by `GET /api/auth/status`.

```python
class AuthStatusResponse(BaseModel):
    authenticated: bool
    phone: Optional[str]
    session_valid: bool
    user_id: Optional[int]
    username: Optional[str]
```

**Example (Authenticated):**

```json
{
  "authenticated": true,
  "phone": "+1234567890",
  "session_valid": true,
  "user_id": 123456789,
  "username": "john_doe"
}
```

**Example (Not Authenticated):**

```json
{
  "authenticated": false,
  "phone": null,
  "session_valid": false,
  "user_id": null,
  "username": null
}
```

---

## 🔄 Type Conversions

### From Domain Model to Response Schema

Convert domain models to API response schemas:

```python
from datetime import datetime
from src.models import Contact, Tag
from src.schemas import ContactResponse, TagResponse

# Convert Contact model to ContactResponse
def contact_to_response(contact: Contact, tag_names: List[str]) -> ContactResponse:
    return ContactResponse(
        id=contact.id,
        telegram_id=contact.telegram_id,
        username=contact.username,
        first_name=contact.first_name,
        last_name=contact.last_name,
        display_name=contact.display_name,
        phone=contact.phone,
        profile_photo_url=f"/api/media/profile-photos/{contact.telegram_id}.jpg" if contact.profile_photo_path else None,
        tags=tag_names,
        updated_at=contact.updated_at
    )

# Convert Tag model to TagResponse
def tag_to_response(tag: Tag, contact_count: int) -> TagResponse:
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        contact_count=contact_count
    )
```

### From Request Schema to Domain Model

Convert API requests to domain models:

```python
from src.schemas import TagCreate
from src.models import Tag

def create_tag_from_request(request: TagCreate) -> Tag:
    return Tag(
        id=None,  # Will be assigned by database
        name=request.name,
        color=request.color,
        created_at=datetime.now()
    )
```

---

## 🧪 Testing Schemas

### Validation Testing

```python
import pytest
from pydantic import ValidationError
from src.schemas import TagCreate

def test_tag_create_valid():
    """Test creating valid tag."""
    tag = TagCreate(name="Work", color="#FF5733")
    assert tag.name == "Work"
    assert tag.color == "#FF5733"

def test_tag_create_invalid_color():
    """Test invalid color raises error."""
    with pytest.raises(ValidationError) as exc_info:
        TagCreate(name="Work", color="invalid")
    
    assert "valid hex color code" in str(exc_info.value)
```

### Serialization Testing

```python
def test_contact_response_serialization():
    """Test ContactResponse can be serialized to JSON."""
    from datetime import datetime
    from src.schemas import ContactResponse
    
    contact = ContactResponse(
        id=1,
        telegram_id=123456789,
        username="john_doe",
        first_name="John",
        last_name="Doe",
        display_name="John Doe",
        phone=None,
        profile_photo_url=None,
        tags=["Work"],
        updated_at=datetime.now()
    )
    
    # Serialize to dict
    data = contact.model_dump()
    assert data["id"] == 1
    assert data["username"] == "john_doe"
    
    # Serialize to JSON
    json_str = contact.model_dump_json()
    assert "john_doe" in json_str
```

---

## 💡 Best Practices

### 1. Always Validate Input

```python
# ✅ Good - Use Pydantic schemas
from fastapi import APIRouter
from src.schemas import TagCreate

router = APIRouter()

@router.post("/tags")
async def create_tag(tag_data: TagCreate):
    # tag_data is already validated
    return {"message": "Tag created"}

# ❌ Bad - Manual validation
@router.post("/tags")
async def create_tag(name: str, color: str):
    # No validation, potential issues
    return {"message": "Tag created"}
```

### 2. Use Response Models

```python
# ✅ Good - Explicitly define response model
from src.schemas import TagResponse

@router.get("/tags/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int) -> TagResponse:
    # Return type is clear and validated
    pass

# ❌ Bad - No response model
@router.get("/tags/{tag_id}")
async def get_tag(tag_id: int):
    # Response type is unclear
    pass
```

### 3. Provide Examples

```python
# ✅ Good - Include examples
class TagCreate(BaseModel):
    name: str = Field(..., examples=["Work", "Personal"])
    color: Optional[str] = Field(None, examples=["#FF5733"])
```

### 4. Use Custom Validators

```python
# ✅ Good - Custom validation logic
from pydantic import field_validator

class TagCreate(BaseModel):
    color: Optional[str] = None
    
    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Invalid hex color")
        return v.upper() if v else v
```

### 5. Handle Optional Fields Properly

```python
# ✅ Good - Clear optional handling
class ContactResponse(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None

# ❌ Bad - Ambiguous
class ContactResponse(BaseModel):
    username: str  # Is None allowed?
    phone: str
```

---

## ⚠️ Common Pitfalls

### 1. Forgetting to Trim Input

```python
# ✅ Correct - Trim whitespace
@field_validator("name")
@classmethod
def validate_name(cls, v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("Name cannot be empty")
    return v
```

### 2. Not Normalizing Data

```python
# ✅ Correct - Normalize color to uppercase
@field_validator("color")
@classmethod
def validate_color(cls, v: Optional[str]) -> Optional[str]:
    if v:
        return v.upper()  # Normalize
    return v
```

### 3. Inconsistent Validation

```python
# ❌ Wrong - Different validation in different places
# Use the same validator everywhere

# ✅ Correct - Consistent validation
# Define validator once, reuse logic
```

---

## 🔗 Related Documentation

- **[Domain Models](./domain-models.md)** - Domain layer models
- **[API Endpoints](./api-endpoints.md)** - REST API routes
- **[Testing Guide](./testing-guide.md)** - How to test schemas
- **[Validation Patterns](./validation-patterns.md)** - Common validation patterns

---

## 📊 Schema Summary

### Total Schemas: 14

#### Contact Schemas (4)
- `ContactResponse`
- `ContactProfileResponse`
- `GroupInfo`
- `MessageInfo`

#### Tag Schemas (3)
- `TagCreate`
- `TagUpdate`
- `TagResponse`

#### Message Schemas (5)
- `SendMessageRequest`
- `BulkMessageRequest`
- `MessageResult`
- `BulkMessageJob`
- `BulkMessageStatus`

#### Auth Schemas (5)
- `AuthInitRequest`
- `AuthCodeRequest`
- `AuthPasswordRequest`
- `AuthResponse`
- `AuthStatusResponse`

---

## 🎯 Quick Reference

### Validation Patterns

```python
# String length
Field(..., min_length=1, max_length=50)

# Positive integer
Field(..., gt=0)

# List with minimum items
Field(..., min_length=1)

# Custom validator
@field_validator("field_name")
@classmethod
def validate_field(cls, v):
    # Validation logic
    return v

# Hex color validation
if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
    raise ValueError("Invalid hex color")

# Phone validation
if not re.match(r"^\+[1-9]\d{1,14}$", v):
    raise ValueError("Invalid phone number")
```

---

**Next Steps:**
- Review [API Endpoints](./api-endpoints.md) for how schemas are used
- Check [Domain Models](./domain-models.md) for data layer integration
- Explore [Testing Guide](./testing-guide.md) for testing strategies

---

*Last updated: 2024 | Part of Telegram Contact Manager Backend Documentation*
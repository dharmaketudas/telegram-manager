# Domain Models Documentation

**Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** Complete ✅

---

## 📖 Overview

This document provides comprehensive documentation for the domain models used throughout the Telegram Contact Manager application. Domain models are dataclass-based Python objects that represent the core business entities of the application.

### Purpose

Domain models serve as:
- **Data Transfer Objects (DTOs)** - Moving data between layers
- **Type-Safe Containers** - Ensuring data integrity with Python type hints
- **Business Logic Holders** - Containing computed properties and validation
- **Documentation** - Self-documenting data structures

### Location

All domain models are located in the `src/models/` directory:

```
src/models/
├── __init__.py        # Package exports
├── contact.py         # Contact and ContactProfile models
├── group.py           # Group model
├── tag.py             # Tag model
└── message.py         # Message model
```

---

## 🏗️ Architecture

### Design Principles

1. **Immutability by Default** - Use dataclasses with frozen=False for flexibility
2. **Type Safety** - All fields have explicit type hints
3. **Optional Fields** - Use `Optional[T]` for nullable fields
4. **Computed Properties** - Use `@property` for derived values
5. **Rich Representations** - Implement `__str__` and `__repr__` for debugging

### Import Pattern

```python
# Import all models from the package
from src.models import Contact, Group, Tag, Message, ContactProfile

# Or import specific models
from src.models.contact import Contact
from src.models.tag import Tag
```

---

## 📦 Models Reference

### 1. Contact Model

Represents a Telegram user/contact.

#### Definition

```python
@dataclass
class Contact:
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
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `Optional[int]` | No | Internal database ID (None for new contacts) |
| `telegram_id` | `int` | Yes | Unique Telegram user ID |
| `username` | `Optional[str]` | No | Telegram username (without @) |
| `first_name` | `Optional[str]` | No | Contact's first name |
| `last_name` | `Optional[str]` | No | Contact's last name |
| `display_name` | `str` | Yes | Preferred display name |
| `phone` | `Optional[str]` | No | Phone number if available |
| `profile_photo_path` | `Optional[str]` | No | Path to stored profile photo |
| `bio` | `Optional[str]` | No | User's bio/about text |
| `created_at` | `datetime` | Yes | When contact was first discovered |
| `updated_at` | `datetime` | Yes | When contact was last updated |

#### Computed Properties

##### `full_name` → `str`

Generates a full name with intelligent fallback logic:

1. Returns `first_name + last_name` if available
2. Falls back to `username` if no names
3. Falls back to `"User {telegram_id}"` if no username

```python
contact = Contact(
    id=1,
    telegram_id=123456789,
    username="john_doe",
    first_name="John",
    last_name="Doe",
    display_name="John Doe",
    phone=None,
    profile_photo_path=None,
    bio=None,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

print(contact.full_name)  # Output: "John Doe"
```

#### Usage Examples

**Creating a new contact:**

```python
from datetime import datetime
from src.models import Contact

contact = Contact(
    id=None,  # Will be assigned by database
    telegram_id=123456789,
    username="john_doe",
    first_name="John",
    last_name="Doe",
    display_name="John Doe",
    phone="+1234567890",
    profile_photo_path="/media/profiles/123456789.jpg",
    bio="Software Engineer",
    created_at=datetime.now(),
    updated_at=datetime.now()
)
```

**Contact with minimal information:**

```python
contact = Contact(
    id=None,
    telegram_id=987654321,
    username=None,
    first_name=None,
    last_name=None,
    display_name="Unknown User",
    phone=None,
    profile_photo_path=None,
    bio=None,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

print(contact.full_name)  # Output: "User 987654321"
```

#### String Representations

```python
str(contact)   # "Contact(John Doe, @john_doe)"
repr(contact)  # "Contact(id=1, telegram_id=123456789, username=john_doe, full_name=John Doe)"
```

---

### 2. Group Model

Represents a Telegram group or supergroup.

#### Definition

```python
@dataclass
class Group:
    id: Optional[int]
    telegram_id: int
    name: str
    member_count: int
    profile_photo_path: Optional[str]
    created_at: datetime
    updated_at: datetime
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `Optional[int]` | No | Internal database ID (None for new groups) |
| `telegram_id` | `int` | Yes | Unique Telegram group/chat ID |
| `name` | `str` | Yes | Group name |
| `member_count` | `int` | Yes | Number of members in the group |
| `profile_photo_path` | `Optional[str]` | No | Path to stored group profile photo |
| `created_at` | `datetime` | Yes | When group was first discovered |
| `updated_at` | `datetime` | Yes | When group was last updated |

#### Usage Examples

**Creating a group:**

```python
from datetime import datetime
from src.models import Group

group = Group(
    id=None,
    telegram_id=1001234567890,
    name="Python Developers",
    member_count=150,
    profile_photo_path="/media/groups/1001234567890.jpg",
    created_at=datetime.now(),
    updated_at=datetime.now()
)
```

#### String Representations

```python
str(group)   # "Group(Python Developers, 150 members)"
repr(group)  # "Group(id=1, telegram_id=1001234567890, name=Python Developers, member_count=150)"
```

---

### 3. Tag Model

Represents a tag for organizing contacts.

#### Definition

```python
@dataclass
class Tag:
    id: Optional[int]
    name: str
    color: Optional[str]
    created_at: datetime
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `Optional[int]` | No | Internal database ID (None for new tags) |
| `name` | `str` | Yes | Unique tag name |
| `color` | `Optional[str]` | No | Hex color code (e.g., "#FF5733") |
| `created_at` | `datetime` | Yes | When tag was created |

#### Special Behavior

##### Equality and Hashing

Tags are compared by name (case-insensitive) and can be used in sets:

```python
tag1 = Tag(id=1, name="Work", color="#FF5733", created_at=datetime.now())
tag2 = Tag(id=2, name="work", color="#00FF00", created_at=datetime.now())

print(tag1 == tag2)  # True (case-insensitive comparison)

tag_set = {tag1, tag2}
print(len(tag_set))  # 1 (only one unique tag)
```

#### Usage Examples

**Creating a tag with color:**

```python
from datetime import datetime
from src.models import Tag

tag = Tag(
    id=None,
    name="Work",
    color="#FF5733",
    created_at=datetime.now()
)
```

**Creating a tag without color:**

```python
tag = Tag(
    id=None,
    name="Personal",
    color=None,
    created_at=datetime.now()
)
```

#### String Representations

```python
# With color
str(tag)   # "Tag(Work (#FF5733))"

# Without color
str(tag)   # "Tag(Personal)"

repr(tag)  # "Tag(id=1, name=Work, color=#FF5733, created_at=2024-01-01 12:00:00)"
```

---

### 4. Message Model

Represents a message exchanged with a contact.

#### Definition

```python
@dataclass
class Message:
    id: Optional[int]
    telegram_message_id: Optional[int]
    contact_id: int
    is_outgoing: bool
    content: Optional[str]
    timestamp: datetime
    created_at: datetime
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `Optional[int]` | No | Internal database ID (None for new messages) |
| `telegram_message_id` | `Optional[int]` | No | Telegram's unique message ID |
| `contact_id` | `int` | Yes | ID of associated contact |
| `is_outgoing` | `bool` | Yes | True if sent by user, False if received |
| `content` | `Optional[str]` | No | Text content of the message |
| `timestamp` | `datetime` | Yes | When message was sent/received |
| `created_at` | `datetime` | Yes | When record was created in database |

#### Computed Properties

##### `direction` → `str`

Returns a human-readable direction indicator:

```python
message.direction  # "sent" if outgoing, "received" if incoming
```

##### `preview` → `str`

Returns a preview of the message content (max 100 chars):

```python
long_message = Message(
    id=1,
    telegram_message_id=12345,
    contact_id=10,
    is_outgoing=True,
    content="A" * 150,  # 150 character string
    timestamp=datetime.now(),
    created_at=datetime.now()
)

print(long_message.preview)  # "AAAA...AAAA..." (100 chars + "...")
```

For messages without content:

```python
empty_message = Message(
    id=1,
    telegram_message_id=12345,
    contact_id=10,
    is_outgoing=True,
    content=None,
    timestamp=datetime.now(),
    created_at=datetime.now()
)

print(empty_message.preview)  # "[No content]"
```

#### Usage Examples

**Creating an outgoing message:**

```python
from datetime import datetime
from src.models import Message

message = Message(
    id=None,
    telegram_message_id=12345,
    contact_id=10,
    is_outgoing=True,
    content="Hello, how are you?",
    timestamp=datetime.now(),
    created_at=datetime.now()
)
```

**Creating an incoming message:**

```python
message = Message(
    id=None,
    telegram_message_id=12346,
    contact_id=10,
    is_outgoing=False,
    content="I'm doing great, thanks!",
    timestamp=datetime.now(),
    created_at=datetime.now()
)
```

**Media-only message (no text content):**

```python
message = Message(
    id=None,
    telegram_message_id=12347,
    contact_id=10,
    is_outgoing=True,
    content=None,  # Photo/video/file with no caption
    timestamp=datetime.now(),
    created_at=datetime.now()
)
```

#### String Representations

```python
# Outgoing message
str(message)  # "Message(→ Hello, how are you?)"

# Incoming message
str(message)  # "Message(← I'm doing great!)"

repr(message)  # "Message(id=1, telegram_message_id=12345, contact_id=10, is_outgoing=True, timestamp=...)"
```

---

### 5. ContactProfile Model

Aggregated view combining contact data with related entities.

#### Definition

```python
@dataclass
class ContactProfile:
    contact: Contact
    tags: List[Tag]
    mutual_groups: List[Group]
    last_received_message: Optional[Message]
    last_sent_message: Optional[Message]
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contact` | `Contact` | Yes | The contact object |
| `tags` | `List[Tag]` | Yes | Tags assigned to this contact |
| `mutual_groups` | `List[Group]` | Yes | Groups where both user and contact are members |
| `last_received_message` | `Optional[Message]` | No | Most recent message received from contact |
| `last_sent_message` | `Optional[Message]` | No | Most recent message sent to contact |

#### Usage Examples

**Creating a complete profile:**

```python
from datetime import datetime
from src.models import Contact, ContactProfile, Tag, Group, Message

# Create contact
contact = Contact(
    id=1,
    telegram_id=123456789,
    username="john_doe",
    first_name="John",
    last_name="Doe",
    display_name="John Doe",
    phone=None,
    profile_photo_path=None,
    bio=None,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

# Create tags
tags = [
    Tag(id=1, name="Work", color="#FF5733", created_at=datetime.now()),
    Tag(id=2, name="Friend", color="#00FF00", created_at=datetime.now())
]

# Create mutual groups
groups = [
    Group(
        id=1,
        telegram_id=111,
        name="Python Developers",
        member_count=100,
        profile_photo_path=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
]

# Create messages
last_received = Message(
    id=1,
    telegram_message_id=12345,
    contact_id=1,
    is_outgoing=False,
    content="Hey there!",
    timestamp=datetime.now(),
    created_at=datetime.now()
)

last_sent = Message(
    id=2,
    telegram_message_id=12346,
    contact_id=1,
    is_outgoing=True,
    content="Hi! How are you?",
    timestamp=datetime.now(),
    created_at=datetime.now()
)

# Create profile
profile = ContactProfile(
    contact=contact,
    tags=tags,
    mutual_groups=groups,
    last_received_message=last_received,
    last_sent_message=last_sent
)
```

**Profile with no activity:**

```python
profile = ContactProfile(
    contact=contact,
    tags=[],
    mutual_groups=[],
    last_received_message=None,
    last_sent_message=None
)
```

#### String Representations

```python
str(profile)  # "ContactProfile(John Doe, 2 tags, 1 mutual groups)"
```

---

## 🔄 Type Conversions

### From Database Row to Model

When retrieving data from the database, convert rows to models:

```python
async def get_contact_by_id(contact_id: int) -> Optional[Contact]:
    async with get_db_connection() as conn:
        cursor = await conn.execute(
            "SELECT * FROM contacts WHERE id = ?",
            (contact_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        return Contact(
            id=row[0],
            telegram_id=row[1],
            username=row[2],
            first_name=row[3],
            last_name=row[4],
            display_name=row[5],
            phone=row[6],
            profile_photo_path=row[7],
            bio=row[8],
            created_at=datetime.fromisoformat(row[9]),
            updated_at=datetime.fromisoformat(row[10])
        )
```

### From Model to Database

When saving models to the database:

```python
async def create_contact(contact: Contact) -> int:
    async with get_db_connection() as conn:
        cursor = await conn.execute(
            """
            INSERT INTO contacts (
                telegram_id, username, first_name, last_name,
                display_name, phone, profile_photo_path, bio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                contact.telegram_id,
                contact.username,
                contact.first_name,
                contact.last_name,
                contact.display_name,
                contact.phone,
                contact.profile_photo_path,
                contact.bio
            )
        )
        await conn.commit()
        return cursor.lastrowid
```

---

## 🧪 Testing Models

### Unit Test Example

```python
import pytest
from datetime import datetime
from src.models import Contact

class TestContact:
    def test_contact_creation(self):
        now = datetime.now()
        contact = Contact(
            id=1,
            telegram_id=123456789,
            username="john_doe",
            first_name="John",
            last_name="Doe",
            display_name="John Doe",
            phone=None,
            profile_photo_path=None,
            bio=None,
            created_at=now,
            updated_at=now
        )
        
        assert contact.id == 1
        assert contact.telegram_id == 123456789
        assert contact.full_name == "John Doe"
    
    def test_full_name_fallback(self):
        now = datetime.now()
        contact = Contact(
            id=1,
            telegram_id=123456789,
            username="john_doe",
            first_name=None,
            last_name=None,
            display_name="john_doe",
            phone=None,
            profile_photo_path=None,
            bio=None,
            created_at=now,
            updated_at=now
        )
        
        assert contact.full_name == "john_doe"
```

---

## 💡 Best Practices

### 1. Always Use Type Hints

```python
# ✅ Good
def create_contact(contact: Contact) -> int:
    pass

# ❌ Bad
def create_contact(contact):
    pass
```

### 2. Handle Optional Fields

```python
# ✅ Good
if contact.username:
    print(f"Username: {contact.username}")

# ❌ Bad
print(f"Username: {contact.username}")  # May print "None"
```

### 3. Use Computed Properties

```python
# ✅ Good
display_name = contact.full_name  # Uses computed property

# ❌ Bad
display_name = f"{contact.first_name} {contact.last_name}"  # Doesn't handle None
```

### 4. Validate Data Before Creating Models

```python
# ✅ Good
if telegram_id and display_name:
    contact = Contact(
        id=None,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        display_name=display_name or f"User {telegram_id}",
        phone=phone,
        profile_photo_path=None,
        bio=bio,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
```

### 5. Use Dataclass Features

```python
from dataclasses import asdict, replace

# Convert to dictionary
contact_dict = asdict(contact)

# Create a modified copy
updated_contact = replace(contact, username="new_username")
```

---

## 🔗 Related Documentation

- **[Database Schema](./database-schema.md)** - Database table definitions
- **[Repository Layer](./repositories.md)** - Data access patterns
- **[API Schemas](./api-schemas.md)** - Pydantic validation schemas
- **[Testing Guide](./testing-guide.md)** - How to test models

---

## 📝 Notes

### Datetime Handling

All datetime fields use Python's `datetime` objects. When storing in SQLite:

```python
# Storing
datetime_str = contact.created_at.isoformat()

# Retrieving
created_at = datetime.fromisoformat(row["created_at"])
```

### Null vs Empty String

For optional string fields, prefer `None` over empty strings:

```python
# ✅ Good
contact.username = None

# ❌ Bad
contact.username = ""
```

### Model Equality

Models use default dataclass equality (compare all fields):

```python
contact1 = Contact(id=1, telegram_id=123, ...)
contact2 = Contact(id=1, telegram_id=123, ...)

print(contact1 == contact2)  # True if all fields match
```

---

## ⚠️ Common Pitfalls

### 1. Forgetting Optional Type Hints

```python
# ❌ Wrong
username: str  # Will raise error if None

# ✅ Correct
username: Optional[str]  # Allows None
```

### 2. Mutating Shared Lists

```python
# ❌ Wrong
default_tags = []
profile1 = ContactProfile(contact, default_tags, [], None, None)
profile2 = ContactProfile(contact, default_tags, [], None, None)
# Both profiles share the same list!

# ✅ Correct
profile1 = ContactProfile(contact, [], [], None, None)
profile2 = ContactProfile(contact, [], [], None, None)
```

### 3. Not Handling None in Computed Properties

```python
# The full_name property handles this correctly:
@property
def full_name(self) -> str:
    parts = [self.first_name, self.last_name]
    name = " ".join(filter(None, parts))  # Filters out None values
    # ... fallback logic
```

---

## 🎯 Quick Reference

### Model Creation Checklist

- [ ] All required fields provided
- [ ] Optional fields explicitly set to None or value
- [ ] Datetime objects created (not strings)
- [ ] Type hints match field types
- [ ] IDs set to None for new entities

### Common Patterns

```python
# Creating new entity (no ID)
entity = Model(id=None, ...)

# Loading from database (with ID)
entity = Model(id=row_id, ...)

# Checking if entity is persisted
if entity.id is not None:
    # Entity exists in database

# Updating timestamp
entity = replace(entity, updated_at=datetime.now())
```

---

**Next Steps:**
- Review [Database Schema](./database-schema.md) for table structures
- Explore [Repository Layer](./repositories.md) for data access
- Check [API Schemas](./api-schemas.md) for REST API contracts

---

*Last updated: 2024 | Part of Telegram Contact Manager Backend Documentation*
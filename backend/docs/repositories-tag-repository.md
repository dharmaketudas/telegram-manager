# Tag Repository Documentation

**Module:** `src.repositories.tag_repository`  
**Class:** `TagRepository`  
**Version:** 1.0.0  
**Last Updated:** 2024

---

## Overview

The `TagRepository` provides asynchronous CRUD operations for tags and manages the many-to-many relationship between contacts and tags using SQLAlchemy ORM. It enables efficient tag-based organization and filtering of contacts.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Class Reference](#class-reference)
4. [Methods](#methods)
5. [Usage Examples](#usage-examples)
6. [Database Schema](#database-schema)
7. [Error Handling](#error-handling)
8. [Testing](#testing)
9. [Best Practices](#best-practices)

---

## Features

### Core CRUD Operations
- ✅ Create tags with unique names and optional colors
- ✅ Retrieve tags by ID or name (case-insensitive)
- ✅ Get all tags with optional pagination
- ✅ Update tag properties (name, color)
- ✅ Delete tags with cascade deletion of associations

### Association Management
- ✅ Add tags to contacts
- ✅ Remove tags from contacts
- ✅ Get all tags for a specific contact
- ✅ Get all contacts for a specific tag
- ✅ Get contacts matching multiple tags (OR operation)
- ✅ Prevent duplicate associations

### Utility Methods
- ✅ Count tags per contact
- ✅ Count contacts per tag
- ✅ Check tag existence by name
- ✅ Automatic timestamp management

---

## Architecture

### Dependencies

```python
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.tag import Tag, contact_tags
from src.models.contact import Contact
```

### Database Tables

The repository manages two tables:

1. **`tags`** - Stores tag definitions
2. **`contact_tags`** - Junction table for many-to-many relationships

### Design Patterns

- **Repository Pattern**: Encapsulates data access logic
- **Async/Await**: Non-blocking database operations
- **ORM Pattern**: Uses SQLAlchemy for object-relational mapping
- **Transaction Management**: Automatic commit/rollback

---

## Class Reference

```python
class TagRepository:
    """
    Asynchronous repository for Tag entities with comprehensive operations.
    
    Provides methods for creating, reading, updating, and deleting tags,
    as well as managing the many-to-many relationship between contacts and tags.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with an async database session.
        
        Args:
            session (AsyncSession): Async SQLAlchemy database session
        """
```

---

## Methods

### CRUD Operations

#### `create(tag_data: Dict[str, Any]) -> Tag`

Create a new tag.

**Parameters:**
- `tag_data` (Dict): Tag data containing:
  - `name` (str, required): Unique tag name
  - `color` (str, optional): Hex color code (e.g., "#FF5733")
  - `created_at` (datetime, optional): Creation timestamp (auto-set if not provided)

**Returns:**
- `Tag`: The newly created tag

**Raises:**
- `ValueError`: If tag creation fails or name already exists

**Example:**
```python
tag_data = {
    "name": "Friends",
    "color": "#FF5733"
}
tag = await tag_repository.create(tag_data)
```

---

#### `get_by_id(tag_id: int) -> Optional[Tag]`

Retrieve a tag by its database ID.

**Parameters:**
- `tag_id` (int): The unique database ID of the tag

**Returns:**
- `Optional[Tag]`: The tag if found, None otherwise

**Example:**
```python
tag = await tag_repository.get_by_id(1)
if tag:
    print(f"Found tag: {tag.name}")
```

---

#### `get_by_name(name: str) -> Optional[Tag]`

Retrieve a tag by its name (case-insensitive).

**Parameters:**
- `name` (str): The tag name to search for

**Returns:**
- `Optional[Tag]`: The tag if found, None otherwise

**Example:**
```python
# These all return the same tag
tag = await tag_repository.get_by_name("Friends")
tag = await tag_repository.get_by_name("FRIENDS")
tag = await tag_repository.get_by_name("fRiEnDs")
```

---

#### `get_all(limit: Optional[int] = None, offset: int = 0) -> List[Tag]`

Retrieve all tags with optional pagination.

**Parameters:**
- `limit` (Optional[int]): Maximum number of records to return
- `offset` (int): Number of records to skip (default: 0)

**Returns:**
- `List[Tag]`: List of tags ordered by name

**Example:**
```python
# Get all tags
all_tags = await tag_repository.get_all()

# Get paginated results
page_1 = await tag_repository.get_all(limit=10, offset=0)
page_2 = await tag_repository.get_all(limit=10, offset=10)
```

---

#### `update(tag_id: int, update_data: Dict[str, Any]) -> Optional[Tag]`

Update an existing tag.

**Parameters:**
- `tag_id` (int): ID of the tag to update
- `update_data` (Dict): Fields to update (name, color)

**Returns:**
- `Optional[Tag]`: Updated tag, or None if not found

**Raises:**
- `ValueError`: If update fails or new name already exists

**Example:**
```python
updated_tag = await tag_repository.update(
    tag_id=1,
    update_data={"color": "#00FF00"}
)
```

---

#### `delete(tag_id: int) -> bool`

Delete a tag by its database ID. This will also remove all contact-tag associations due to CASCADE delete.

**Parameters:**
- `tag_id` (int): ID of the tag to delete

**Returns:**
- `bool`: True if tag was deleted, False if not found

**Example:**
```python
success = await tag_repository.delete(tag_id=1)
if success:
    print("Tag deleted successfully")
```

---

### Association Management

#### `add_tag_to_contact(contact_id: int, tag_id: int) -> bool`

Add a tag to a contact (create association).

**Parameters:**
- `contact_id` (int): The database ID of the contact
- `tag_id` (int): The database ID of the tag

**Returns:**
- `bool`: True if association was created, False if it already existed

**Raises:**
- `ValueError`: If contact or tag doesn't exist

**Example:**
```python
try:
    success = await tag_repository.add_tag_to_contact(
        contact_id=123,
        tag_id=5
    )
    if success:
        print("Tag added to contact")
    else:
        print("Tag was already associated with contact")
except ValueError as e:
    print(f"Error: {e}")
```

---

#### `remove_tag_from_contact(contact_id: int, tag_id: int) -> bool`

Remove a tag from a contact (delete association).

**Parameters:**
- `contact_id` (int): The database ID of the contact
- `tag_id` (int): The database ID of the tag

**Returns:**
- `bool`: True if association was removed, False if it didn't exist

**Example:**
```python
success = await tag_repository.remove_tag_from_contact(
    contact_id=123,
    tag_id=5
)
```

---

#### `get_tags_for_contact(contact_id: int) -> List[Tag]`

Retrieve all tags associated with a specific contact.

**Parameters:**
- `contact_id` (int): The database ID of the contact

**Returns:**
- `List[Tag]`: List of tags assigned to the contact, ordered by name

**Example:**
```python
tags = await tag_repository.get_tags_for_contact(contact_id=123)
for tag in tags:
    print(f"Tag: {tag.name} ({tag.color})")
```

---

#### `get_contacts_by_tag(tag_id: int) -> List[Contact]`

Retrieve all contacts associated with a specific tag.

**Parameters:**
- `tag_id` (int): The database ID of the tag

**Returns:**
- `List[Contact]`: List of contacts with this tag, ordered by display_name

**Example:**
```python
contacts = await tag_repository.get_contacts_by_tag(tag_id=5)
print(f"Found {len(contacts)} contacts with this tag")
```

---

#### `get_contacts_by_tags(tag_ids: List[int]) -> List[Contact]`

Retrieve all contacts that have ANY of the specified tags (OR operation).

**Parameters:**
- `tag_ids` (List[int]): List of tag IDs to filter by

**Returns:**
- `List[Contact]`: List of unique contacts with any of the specified tags

**Example:**
```python
# Get all contacts tagged as "Friends" OR "Family"
contacts = await tag_repository.get_contacts_by_tags(
    tag_ids=[friends_tag_id, family_tag_id]
)
```

---

### Utility Methods

#### `get_tag_count_for_contact(contact_id: int) -> int`

Get the number of tags assigned to a contact.

**Parameters:**
- `contact_id` (int): The database ID of the contact

**Returns:**
- `int`: Number of tags assigned to the contact

**Example:**
```python
count = await tag_repository.get_tag_count_for_contact(contact_id=123)
print(f"Contact has {count} tags")
```

---

#### `get_contact_count_for_tag(tag_id: int) -> int`

Get the number of contacts assigned to a tag.

**Parameters:**
- `tag_id` (int): The database ID of the tag

**Returns:**
- `int`: Number of contacts with this tag

**Example:**
```python
count = await tag_repository.get_contact_count_for_tag(tag_id=5)
print(f"Tag has {count} contacts")
```

---

#### `exists_by_name(name: str) -> bool`

Check if a tag exists with the given name (case-insensitive).

**Parameters:**
- `name` (str): Tag name to check

**Returns:**
- `bool`: True if tag exists, False otherwise

**Example:**
```python
if await tag_repository.exists_by_name("Friends"):
    print("Tag already exists")
else:
    # Safe to create new tag
    await tag_repository.create({"name": "Friends"})
```

---

## Usage Examples

### Complete Workflow Example

```python
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.tag_repository import TagRepository
from src.database.connection import get_db_connection

async def tag_management_example():
    """Complete example of tag management."""
    
    # Get database session
    async with get_db_connection() as db:
        # Create repository instance
        tag_repo = TagRepository(db)
        
        # 1. Create tags
        work_tag = await tag_repo.create({
            "name": "Work",
            "color": "#3498DB"
        })
        
        friends_tag = await tag_repo.create({
            "name": "Friends",
            "color": "#FF5733"
        })
        
        # 2. Get all tags
        all_tags = await tag_repo.get_all()
        print(f"Total tags: {len(all_tags)}")
        
        # 3. Add tags to a contact
        contact_id = 123
        await tag_repo.add_tag_to_contact(contact_id, work_tag.id)
        await tag_repo.add_tag_to_contact(contact_id, friends_tag.id)
        
        # 4. Get contact's tags
        contact_tags = await tag_repo.get_tags_for_contact(contact_id)
        print(f"Contact has {len(contact_tags)} tags")
        
        # 5. Get all contacts with "Work" tag
        work_contacts = await tag_repo.get_contacts_by_tag(work_tag.id)
        print(f"Found {len(work_contacts)} work contacts")
        
        # 6. Update tag color
        await tag_repo.update(work_tag.id, {"color": "#2ECC71"})
        
        # 7. Remove tag from contact
        await tag_repo.remove_tag_from_contact(contact_id, friends_tag.id)
        
        # 8. Get statistics
        tag_count = await tag_repo.get_tag_count_for_contact(contact_id)
        contact_count = await tag_repo.get_contact_count_for_tag(work_tag.id)
        
        print(f"Contact has {tag_count} tags")
        print(f"Work tag has {contact_count} contacts")
```

---

### Bulk Messaging Use Case

```python
async def send_message_to_tagged_contacts(tag_names: List[str], message: str):
    """Send a message to all contacts with specific tags."""
    
    async with get_db_connection() as db:
        tag_repo = TagRepository(db)
        
        # Get tag IDs by name
        tag_ids = []
        for tag_name in tag_names:
            tag = await tag_repo.get_by_name(tag_name)
            if tag:
                tag_ids.append(tag.id)
        
        if not tag_ids:
            print("No tags found")
            return
        
        # Get all contacts with any of these tags
        contacts = await tag_repo.get_contacts_by_tags(tag_ids)
        
        print(f"Sending message to {len(contacts)} contacts...")
        
        # Send message to each contact
        for contact in contacts:
            # Send message logic here
            print(f"Sending to: {contact.display_name}")
```

---

### Tag Management UI Helper

```python
async def get_tag_statistics():
    """Get statistics for tag management UI."""
    
    async with get_db_connection() as db:
        tag_repo = TagRepository(db)
        
        all_tags = await tag_repo.get_all()
        
        stats = []
        for tag in all_tags:
            contact_count = await tag_repo.get_contact_count_for_tag(tag.id)
            stats.append({
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "contact_count": contact_count
            })
        
        # Sort by contact count (most popular first)
        stats.sort(key=lambda x: x["contact_count"], reverse=True)
        
        return stats
```

---

## Database Schema

### Tags Table

```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tags_name ON tags(name);
```

### Contact Tags Junction Table

```sql
CREATE TABLE contact_tags (
    contact_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contact_id, tag_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX idx_contact_tags_contact_id ON contact_tags(contact_id);
CREATE INDEX idx_contact_tags_tag_id ON contact_tags(tag_id);
```

### Schema Diagram

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│    contacts     │         │  contact_tags    │         │      tags       │
├─────────────────┤         ├──────────────────┤         ├─────────────────┤
│ id (PK)         │◄────────┤ contact_id (FK)  │         │ id (PK)         │
│ telegram_id     │         │ tag_id (FK)      ├────────►│ name (UNIQUE)   │
│ username        │         │ created_at       │         │ color           │
│ display_name    │         └──────────────────┘         │ created_at      │
│ ...             │                                       └─────────────────┘
└─────────────────┘
```

---

## Error Handling

### Common Exceptions

#### ValueError - Duplicate Tag Name

```python
try:
    tag = await tag_repo.create({"name": "Work"})
except ValueError as e:
    if "already exists" in str(e):
        print("Tag with this name already exists")
```

#### ValueError - Non-Existent Contact or Tag

```python
try:
    await tag_repo.add_tag_to_contact(contact_id=999, tag_id=1)
except ValueError as e:
    if "not found" in str(e):
        print("Contact or tag doesn't exist")
```

### Best Practices for Error Handling

```python
async def safe_tag_creation(name: str, color: str = None):
    """Safely create a tag with error handling."""
    
    try:
        # Check if tag exists first
        if await tag_repo.exists_by_name(name):
            print(f"Tag '{name}' already exists")
            return await tag_repo.get_by_name(name)
        
        # Create new tag
        return await tag_repo.create({
            "name": name,
            "color": color
        })
        
    except ValueError as e:
        print(f"Failed to create tag: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

---

## Testing

### Test Coverage

The `TagRepository` has comprehensive test coverage with 38 unit tests:

- ✅ Tag creation (4 tests)
- ✅ Tag retrieval (8 tests)
- ✅ Tag updates (4 tests)
- ✅ Tag deletion (2 tests)
- ✅ Association management (10 tests)
- ✅ Count operations (4 tests)
- ✅ Helper methods (3 tests)
- ✅ Cascade deletion (1 test)

### Running Tests

```bash
# Run all tag repository tests
pytest tests/unit/test_tag_repository.py -v

# Run specific test class
pytest tests/unit/test_tag_repository.py::TestTagRepositoryCreate -v

# Run with coverage
pytest tests/unit/test_tag_repository.py --cov=src.repositories.tag_repository
```

### Example Test

```python
@pytest.mark.asyncio
async def test_add_tag_to_contact(tag_repository, sample_contact, sample_tag):
    """Test adding a tag to a contact."""
    result = await tag_repository.add_tag_to_contact(
        sample_contact.id, sample_tag.id
    )
    
    assert result is True
    
    # Verify the association exists
    tags = await tag_repository.get_tags_for_contact(sample_contact.id)
    assert len(tags) == 1
    assert tags[0].id == sample_tag.id
```

---

## Best Practices

### 1. Use Exists Check Before Creation

```python
# Good ✅
if not await tag_repo.exists_by_name("Friends"):
    tag = await tag_repo.create({"name": "Friends"})
else:
    tag = await tag_repo.get_by_name("Friends")

# Bad ❌ - May raise exception
tag = await tag_repo.create({"name": "Friends"})
```

### 2. Check Return Values for Association Operations

```python
# Good ✅
success = await tag_repo.add_tag_to_contact(contact_id, tag_id)
if success:
    print("Association created")
else:
    print("Association already existed")

# Bad ❌ - Ignores duplicate check
await tag_repo.add_tag_to_contact(contact_id, tag_id)
```

### 3. Use Case-Insensitive Name Searches

```python
# Good ✅ - Case-insensitive
tag = await tag_repo.get_by_name("friends")

# Bad ❌ - Case-sensitive won't work
tag = await tag_repo.get_by_id_where_name_exact("friends")
```

### 4. Batch Operations with Transaction

```python
# Good ✅ - All or nothing
async with db.transaction():
    for tag_id in tag_ids:
        await tag_repo.add_tag_to_contact(contact_id, tag_id)

# Bad ❌ - Partial failures possible
for tag_id in tag_ids:
    await tag_repo.add_tag_to_contact(contact_id, tag_id)
```

### 5. Pagination for Large Result Sets

```python
# Good ✅ - Paginated
page_size = 50
offset = 0
while True:
    tags = await tag_repo.get_all(limit=page_size, offset=offset)
    if not tags:
        break
    process_tags(tags)
    offset += page_size

# Bad ❌ - May load thousands of records
all_tags = await tag_repo.get_all()
```

### 6. Verify Existence Before Deletion

```python
# Good ✅
tag = await tag_repo.get_by_id(tag_id)
if tag:
    success = await tag_repo.delete(tag_id)
else:
    print("Tag not found")

# Acceptable ✅ - Check return value
success = await tag_repo.delete(tag_id)
if not success:
    print("Tag not found")
```

---

## Performance Considerations

### Indexes

The following indexes optimize query performance:

- `idx_tags_name` - Tag name lookups (case-insensitive)
- `idx_contact_tags_contact_id` - Contact-to-tags queries
- `idx_contact_tags_tag_id` - Tag-to-contacts queries

### Query Optimization

#### Get Contacts by Multiple Tags

```python
# Efficient ✅ - Single query with IN clause
contacts = await tag_repo.get_contacts_by_tags([1, 2, 3, 4, 5])

# Inefficient ❌ - Multiple queries
all_contacts = []
for tag_id in [1, 2, 3, 4, 5]:
    contacts = await tag_repo.get_contacts_by_tag(tag_id)
    all_contacts.extend(contacts)
```

#### Counting Before Loading

```python
# Efficient ✅ - Count first
count = await tag_repo.get_contact_count_for_tag(tag_id)
if count > 0:
    contacts = await tag_repo.get_contacts_by_tag(tag_id)

# Inefficient ❌ - Always loads
contacts = await tag_repo.get_contacts_by_tag(tag_id)
if len(contacts) > 0:
    process_contacts(contacts)
```

---

## Migration History

- **Migration 001**: Initial schema with tags and contact_tags tables
- **Migration 006**: Tag Repository implementation documentation

---

## Related Documentation

- [Contact Repository](./repositories-contact-repository.md)
- [Database Schema](./database-schema.md)
- [Domain Models - Tag](./domain-models.md#tag-model)
- [API Schemas - Tag](./api-schemas.md#tag-schemas)
- [Migration System](./migrations-overview.md)

---

## Support

For issues or questions:
1. Check the test files for working examples
2. Review the source code with inline documentation
3. Consult the design specifications in `.claude/specs/`

---

**Version History:**
- v1.0.0 (2024) - Initial Tag Repository implementation with full test coverage
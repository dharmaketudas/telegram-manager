# Database Schema Documentation

Complete documentation of the Telegram Contact Manager database schema.

---

## Overview

The Telegram Contact Manager uses SQLite as its database engine with an async interface via aiosqlite. The schema is designed to efficiently store and manage Telegram contacts, groups, tags, messages, and application state.

### Key Features

- **8 Core Tables** - Normalized schema with proper relationships
- **Foreign Key Constraints** - Data integrity with CASCADE delete
- **15+ Performance Indexes** - Optimized query performance
- **3 Automatic Triggers** - Timestamp management
- **WAL Journal Mode** - Better concurrency support
- **Migration System** - Version-controlled schema changes

---

## Schema Overview

```
┌─────────────┐
│  contacts   │──┐
└─────────────┘  │
                 │  ┌──────────────┐
                 ├──│ contact_tags │──┐
                 │  └──────────────┘  │
                 │                    │  ┌──────┐
                 │                    └──│ tags │
                 │                       └──────┘
                 │  ┌────────────────┐
                 ├──│ contact_groups │──┐
                 │  └────────────────┘  │
                 │                      │  ┌────────┐
                 │                      └──│ groups │
                 │                         └────────┘
                 │  ┌──────────┐
                 └──│ messages │
                    └──────────┘

┌────────────────┐    ┌──────────┐
│ session_config │    │ sync_log │
└────────────────┘    └──────────┘
```

---

## Tables

### 1. contacts

Stores information about Telegram contacts discovered from all chats and groups.

**Purpose:** Central repository for all contact information including profile data.

```sql
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    display_name TEXT NOT NULL,
    phone TEXT,
    profile_photo_path TEXT,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Internal database ID |
| `telegram_id` | INTEGER | UNIQUE, NOT NULL | Telegram user ID |
| `username` | TEXT | - | Telegram username (without @) |
| `first_name` | TEXT | - | User's first name |
| `last_name` | TEXT | - | User's last name |
| `display_name` | TEXT | NOT NULL | Computed display name (first + last or username) |
| `phone` | TEXT | - | Phone number if available |
| `profile_photo_path` | TEXT | - | Path to downloaded profile photo |
| `bio` | TEXT | - | User's bio/about section |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

#### Indexes

- `idx_contacts_telegram_id` - Fast lookup by Telegram ID
- `idx_contacts_username` - Fast lookup by username
- `idx_contacts_display_name` - Fast search by display name

#### Triggers

- `update_contacts_timestamp` - Auto-updates `updated_at` on row modification

#### Usage Examples

```sql
-- Insert a new contact
INSERT INTO contacts (telegram_id, username, first_name, last_name, display_name)
VALUES (123456789, 'johndoe', 'John', 'Doe', 'John Doe');

-- Find contact by username
SELECT * FROM contacts WHERE username = 'johndoe';

-- Find contact by Telegram ID
SELECT * FROM contacts WHERE telegram_id = 123456789;

-- Update contact information
UPDATE contacts 
SET first_name = 'Jonathan', display_name = 'Jonathan Doe'
WHERE telegram_id = 123456789;
```

---

### 2. groups

Stores information about Telegram groups and channels.

**Purpose:** Track mutual groups between the user and their contacts.

```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    member_count INTEGER,
    profile_photo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Internal database ID |
| `telegram_id` | INTEGER | UNIQUE, NOT NULL | Telegram group/channel ID |
| `name` | TEXT | NOT NULL | Group or channel name |
| `member_count` | INTEGER | - | Number of members in the group |
| `profile_photo_path` | TEXT | - | Path to downloaded group photo |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

#### Indexes

- `idx_groups_telegram_id` - Fast lookup by Telegram group ID
- `idx_groups_name` - Fast search by group name

#### Triggers

- `update_groups_timestamp` - Auto-updates `updated_at` on row modification

#### Usage Examples

```sql
-- Insert a new group
INSERT INTO groups (telegram_id, name, member_count)
VALUES (987654321, 'Python Developers', 1500);

-- Find groups by name pattern
SELECT * FROM groups WHERE name LIKE '%Python%';

-- Update member count
UPDATE groups SET member_count = 1600 WHERE telegram_id = 987654321;
```

---

### 3. tags

Stores user-defined tags for organizing contacts.

**Purpose:** Enable custom categorization and filtering of contacts.

```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Internal database ID |
| `name` | TEXT | UNIQUE, NOT NULL | Tag name (e.g., "Family", "Work") |
| `color` | TEXT | - | Hex color code for UI display |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Tag creation timestamp |

#### Indexes

- `idx_tags_name` - Fast lookup and uniqueness enforcement

#### Usage Examples

```sql
-- Create new tags
INSERT INTO tags (name, color) VALUES ('Family', '#FF5733');
INSERT INTO tags (name, color) VALUES ('Work', '#3498DB');

-- Find all tags
SELECT * FROM tags ORDER BY name;

-- Find tag by name
SELECT id FROM tags WHERE name = 'Family';
```

---

### 4. contact_tags

Junction table for many-to-many relationship between contacts and tags.

**Purpose:** Associate multiple tags with each contact and vice versa.

```sql
CREATE TABLE contact_tags (
    contact_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contact_id, tag_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `contact_id` | INTEGER | NOT NULL, FK | Reference to contacts.id |
| `tag_id` | INTEGER | NOT NULL, FK | Reference to tags.id |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When tag was added to contact |

#### Indexes

- `idx_contact_tags_contact_id` - Fast lookup of tags for a contact
- `idx_contact_tags_tag_id` - Fast lookup of contacts with a tag

#### Foreign Keys

- **ON DELETE CASCADE** - Deleting a contact or tag removes associations

#### Usage Examples

```sql
-- Add tag to contact
INSERT INTO contact_tags (contact_id, tag_id) VALUES (1, 2);

-- Find all tags for a contact
SELECT t.* FROM tags t
JOIN contact_tags ct ON t.id = ct.tag_id
WHERE ct.contact_id = 1;

-- Find all contacts with a specific tag
SELECT c.* FROM contacts c
JOIN contact_tags ct ON c.id = ct.contact_id
WHERE ct.tag_id = 2;

-- Remove tag from contact
DELETE FROM contact_tags WHERE contact_id = 1 AND tag_id = 2;
```

---

### 5. contact_groups

Junction table for many-to-many relationship between contacts and groups.

**Purpose:** Track which contacts are in which mutual groups.

```sql
CREATE TABLE contact_groups (
    contact_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contact_id, group_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `contact_id` | INTEGER | NOT NULL, FK | Reference to contacts.id |
| `group_id` | INTEGER | NOT NULL, FK | Reference to groups.id |
| `joined_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When contact joined the group |

#### Indexes

- `idx_contact_groups_contact_id` - Fast lookup of groups for a contact
- `idx_contact_groups_group_id` - Fast lookup of contacts in a group

#### Foreign Keys

- **ON DELETE CASCADE** - Deleting a contact or group removes associations

#### Usage Examples

```sql
-- Add contact to group
INSERT INTO contact_groups (contact_id, group_id) VALUES (1, 3);

-- Find all groups a contact is in
SELECT g.* FROM groups g
JOIN contact_groups cg ON g.id = cg.group_id
WHERE cg.contact_id = 1;

-- Find all contacts in a group
SELECT c.* FROM contacts c
JOIN contact_groups cg ON c.id = cg.contact_id
WHERE cg.group_id = 3;

-- Find mutual groups between contacts
SELECT g.* FROM groups g
JOIN contact_groups cg1 ON g.id = cg1.group_id
JOIN contact_groups cg2 ON g.id = cg2.group_id
WHERE cg1.contact_id = 1 AND cg2.contact_id = 2;
```

---

### 6. messages

Stores message history for contacts.

**Purpose:** Track sent and received messages for conversation history.

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_message_id INTEGER,
    contact_id INTEGER NOT NULL,
    is_outgoing BOOLEAN NOT NULL,
    content TEXT,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Internal database ID |
| `telegram_message_id` | INTEGER | - | Telegram message ID if available |
| `contact_id` | INTEGER | NOT NULL, FK | Reference to contacts.id |
| `is_outgoing` | BOOLEAN | NOT NULL | True if sent by user, False if received |
| `content` | TEXT | - | Message text content |
| `timestamp` | TIMESTAMP | NOT NULL | When message was sent/received |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

#### Indexes

- `idx_messages_contact_id` - Fast lookup of messages for a contact
- `idx_messages_timestamp` - Ordered message retrieval (DESC for recent first)
- `idx_messages_is_outgoing` - Filter by sent/received

#### Foreign Keys

- **ON DELETE CASCADE** - Deleting a contact removes their messages

#### Usage Examples

```sql
-- Insert a message
INSERT INTO messages (contact_id, is_outgoing, content, timestamp)
VALUES (1, 1, 'Hello!', CURRENT_TIMESTAMP);

-- Get recent messages for a contact
SELECT * FROM messages 
WHERE contact_id = 1 
ORDER BY timestamp DESC 
LIMIT 50;

-- Get last message sent to contact
SELECT * FROM messages
WHERE contact_id = 1 AND is_outgoing = 1
ORDER BY timestamp DESC
LIMIT 1;

-- Count messages exchanged with contact
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN is_outgoing = 1 THEN 1 ELSE 0 END) as sent,
    SUM(CASE WHEN is_outgoing = 0 THEN 1 ELSE 0 END) as received
FROM messages
WHERE contact_id = 1;
```

---

### 7. session_config

Stores application configuration and session data.

**Purpose:** Persist application settings and state between restarts.

```sql
CREATE TABLE session_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `key` | TEXT | PRIMARY KEY | Configuration key |
| `value` | TEXT | - | Configuration value (JSON string for complex data) |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

#### Triggers

- `update_session_config_timestamp` - Auto-updates `updated_at` on modification

#### Usage Examples

```sql
-- Store configuration
INSERT OR REPLACE INTO session_config (key, value)
VALUES ('last_sync_time', '2024-01-15 10:30:00');

-- Retrieve configuration
SELECT value FROM session_config WHERE key = 'last_sync_time';

-- Store complex data as JSON
INSERT OR REPLACE INTO session_config (key, value)
VALUES ('app_settings', '{"theme":"dark","notifications":true}');

-- Delete configuration
DELETE FROM session_config WHERE key = 'some_key';
```

---

### 8. sync_log

Tracks synchronization operations with Telegram.

**Purpose:** Audit trail and debugging information for sync operations.

```sql
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_type TEXT NOT NULL,
    status TEXT NOT NULL,
    records_processed INTEGER,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Internal database ID |
| `sync_type` | TEXT | NOT NULL | Type of sync (e.g., 'contacts', 'groups') |
| `status` | TEXT | NOT NULL | Status (e.g., 'success', 'failed', 'in_progress') |
| `records_processed` | INTEGER | - | Number of records processed |
| `error_message` | TEXT | - | Error details if failed |
| `started_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When sync started |
| `completed_at` | TIMESTAMP | - | When sync completed |

#### Indexes

- `idx_sync_log_sync_type` - Filter logs by sync type
- `idx_sync_log_status` - Filter logs by status

#### Usage Examples

```sql
-- Start a sync operation
INSERT INTO sync_log (sync_type, status)
VALUES ('contacts', 'in_progress');

-- Update sync on completion
UPDATE sync_log
SET status = 'success', 
    records_processed = 150,
    completed_at = CURRENT_TIMESTAMP
WHERE id = 1;

-- Record a failed sync
UPDATE sync_log
SET status = 'failed',
    error_message = 'Connection timeout',
    completed_at = CURRENT_TIMESTAMP
WHERE id = 2;

-- Get recent sync history
SELECT * FROM sync_log 
ORDER BY started_at DESC 
LIMIT 10;

-- Get last successful contact sync
SELECT * FROM sync_log
WHERE sync_type = 'contacts' AND status = 'success'
ORDER BY completed_at DESC
LIMIT 1;
```

---

## Relationships

### Entity Relationship Diagram

```
contacts (1) ──────── (*) contact_tags (*) ──────── (1) tags
contacts (1) ──────── (*) contact_groups (*) ──────── (1) groups
contacts (1) ──────── (*) messages
```

### Relationship Details

#### contacts ↔ tags (many-to-many)
- **Via:** `contact_tags` junction table
- **Cascade:** Deleting contact or tag removes the association
- **Use Case:** Organize contacts with custom tags

#### contacts ↔ groups (many-to-many)
- **Via:** `contact_groups` junction table
- **Cascade:** Deleting contact or group removes the association
- **Use Case:** Track mutual group memberships

#### contacts → messages (one-to-many)
- **Direct:** Foreign key in `messages` table
- **Cascade:** Deleting contact removes all their messages
- **Use Case:** Message history per contact

---

## Indexes Summary

Total: **15 indexes** for query optimization

| Table | Index Name | Columns | Purpose |
|-------|-----------|---------|---------|
| contacts | idx_contacts_telegram_id | telegram_id | Lookup by Telegram ID |
| contacts | idx_contacts_username | username | Search by username |
| contacts | idx_contacts_display_name | display_name | Search by name |
| groups | idx_groups_telegram_id | telegram_id | Lookup by Telegram ID |
| groups | idx_groups_name | name | Search by group name |
| tags | idx_tags_name | name | Lookup by tag name |
| contact_tags | idx_contact_tags_contact_id | contact_id | Tags for contact |
| contact_tags | idx_contact_tags_tag_id | tag_id | Contacts with tag |
| contact_groups | idx_contact_groups_contact_id | contact_id | Groups for contact |
| contact_groups | idx_contact_groups_group_id | group_id | Contacts in group |
| messages | idx_messages_contact_id | contact_id | Messages for contact |
| messages | idx_messages_timestamp | timestamp DESC | Recent messages first |
| messages | idx_messages_is_outgoing | is_outgoing | Filter sent/received |
| sync_log | idx_sync_log_sync_type | sync_type | Filter by sync type |
| sync_log | idx_sync_log_status | status | Filter by status |

---

## Triggers Summary

Total: **3 triggers** for automatic timestamp updates

| Trigger Name | Table | Purpose |
|--------------|-------|---------|
| update_contacts_timestamp | contacts | Update `updated_at` on modification |
| update_groups_timestamp | groups | Update `updated_at` on modification |
| update_session_config_timestamp | session_config | Update `updated_at` on modification |

### Trigger Implementation

```sql
CREATE TRIGGER update_contacts_timestamp
AFTER UPDATE ON contacts
FOR EACH ROW
BEGIN
    UPDATE contacts
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
```

---

## Database Configuration

### SQLite Settings

```sql
-- Foreign key enforcement
PRAGMA foreign_keys = ON;

-- Write-Ahead Logging for better concurrency
PRAGMA journal_mode = WAL;

-- Optimize for performance
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
PRAGMA cache_size = -64000;  -- 64MB cache
```

---

## Common Queries

### Contact Management

```sql
-- Get contact with all tags
SELECT c.*, GROUP_CONCAT(t.name) as tags
FROM contacts c
LEFT JOIN contact_tags ct ON c.id = ct.contact_id
LEFT JOIN tags t ON ct.tag_id = t.id
WHERE c.id = 1
GROUP BY c.id;

-- Search contacts by name or username
SELECT * FROM contacts
WHERE display_name LIKE '%john%' OR username LIKE '%john%'
ORDER BY display_name;

-- Get contacts with specific tag
SELECT c.* FROM contacts c
JOIN contact_tags ct ON c.id = ct.contact_id
JOIN tags t ON ct.tag_id = t.id
WHERE t.name = 'Family';
```

### Group Management

```sql
-- Get all mutual groups for a contact
SELECT g.* FROM groups g
JOIN contact_groups cg ON g.id = cg.group_id
WHERE cg.contact_id = 1
ORDER BY g.member_count DESC;

-- Find contacts in a specific group
SELECT c.* FROM contacts c
JOIN contact_groups cg ON c.id = cg.contact_id
WHERE cg.group_id = 1
ORDER BY c.display_name;
```

### Message History

```sql
-- Get conversation with contact (last 50 messages)
SELECT * FROM messages
WHERE contact_id = 1
ORDER BY timestamp DESC
LIMIT 50;

-- Get contacts with recent activity
SELECT c.*, MAX(m.timestamp) as last_message_time
FROM contacts c
JOIN messages m ON c.id = m.contact_id
GROUP BY c.id
ORDER BY last_message_time DESC
LIMIT 10;
```

---

## Best Practices

### 1. Always Use Parameterized Queries

```python
# ✅ Good - prevents SQL injection
await db.execute(
    "SELECT * FROM contacts WHERE telegram_id = ?",
    (telegram_id,)
)

# ❌ Bad - vulnerable to SQL injection
await db.execute(
    f"SELECT * FROM contacts WHERE telegram_id = {telegram_id}"
)
```

### 2. Use Transactions for Multiple Operations

```python
async with db.transaction():
    # All operations succeed or all fail
    await db.execute("INSERT INTO contacts ...")
    await db.execute("INSERT INTO contact_tags ...")
```

### 3. Leverage Indexes

```python
# Fast - uses idx_contacts_telegram_id
SELECT * FROM contacts WHERE telegram_id = 123;

# Slow - no index on bio field
SELECT * FROM contacts WHERE bio LIKE '%developer%';
```

### 4. Clean Up Related Data

Foreign keys with CASCADE handle this automatically:

```python
# Deleting a contact automatically removes:
# - All contact_tags entries
# - All contact_groups entries
# - All messages
await db.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
```

---

## Migration Information

The database schema is managed through the migration system. See:
- [Migration System Overview](./migrations-overview.md)
- [Migration Quick Reference](./migrations-quick-reference.md)
- [Migrations Directory](./migrations/README.md)

Current schema version: **1**

---

## Performance Considerations

### Query Optimization Tips

1. **Use indexes** - All common queries have supporting indexes
2. **Limit results** - Use LIMIT for large result sets
3. **Batch operations** - Use execute_many for bulk inserts
4. **Pagination** - Use LIMIT + OFFSET for large lists
5. **Analyze queries** - Use EXPLAIN QUERY PLAN to verify index usage

### Example: Efficient Pagination

```python
# Good pagination
page_size = 50
offset = page * page_size

contacts = await db.fetch_all(
    "SELECT * FROM contacts ORDER BY display_name LIMIT ? OFFSET ?",
    (page_size, offset)
)
```

---

## Schema Verification

To verify the schema is correct:

```python
from database import verify_schema

# Returns True if all tables exist
is_valid = await verify_schema(db)
```

---

## Additional Resources

- [Database Implementation Guide](./database-implementation.md)
- [Getting Started](./getting-started.md)
- [API Documentation](http://localhost:8000/docs)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

**Database schema is production-ready and optimized for performance.** ✅
"""
Unit tests for domain models.

This module contains tests for Contact, Group, Tag, Message, and ContactProfile
dataclass models to ensure they behave correctly.
"""

import pytest
from datetime import datetime
from src.models.contact import Contact, ContactProfile
from src.models.group import Group
from src.models.tag import Tag
from src.models.message import Message


class TestContact:
    """Tests for the Contact model."""

    def test_contact_creation_with_all_fields(self):
        """Test creating a contact with all fields populated."""
        now = datetime.now()
        contact = Contact(
            id=1,
            telegram_id=123456789,
            username="john_doe",
            first_name="John",
            last_name="Doe",
            display_name="John Doe",
            phone="+1234567890",
            profile_photo_path="/path/to/photo.jpg",
            bio="Software Developer",
            created_at=now,
            updated_at=now,
        )

        assert contact.id == 1
        assert contact.telegram_id == 123456789
        assert contact.username == "john_doe"
        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
        assert contact.display_name == "John Doe"
        assert contact.phone == "+1234567890"
        assert contact.profile_photo_path == "/path/to/photo.jpg"
        assert contact.bio == "Software Developer"
        assert contact.created_at == now
        assert contact.updated_at == now

    def test_contact_creation_with_minimal_fields(self):
        """Test creating a contact with only required fields."""
        now = datetime.now()
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
            created_at=now,
            updated_at=now,
        )

        assert contact.id is None
        assert contact.telegram_id == 987654321
        assert contact.username is None
        assert contact.first_name is None
        assert contact.last_name is None
        assert contact.display_name == "Unknown User"

    def test_full_name_with_first_and_last(self):
        """Test full_name property with both first and last names."""
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
            updated_at=now,
        )

        assert contact.full_name == "John Doe"

    def test_full_name_with_first_only(self):
        """Test full_name property with only first name."""
        now = datetime.now()
        contact = Contact(
            id=1,
            telegram_id=123456789,
            username="john_doe",
            first_name="John",
            last_name=None,
            display_name="John",
            phone=None,
            profile_photo_path=None,
            bio=None,
            created_at=now,
            updated_at=now,
        )

        assert contact.full_name == "John"

    def test_full_name_with_last_only(self):
        """Test full_name property with only last name."""
        now = datetime.now()
        contact = Contact(
            id=1,
            telegram_id=123456789,
            username="john_doe",
            first_name=None,
            last_name="Doe",
            display_name="Doe",
            phone=None,
            profile_photo_path=None,
            bio=None,
            created_at=now,
            updated_at=now,
        )

        assert contact.full_name == "Doe"

    def test_full_name_fallback_to_username(self):
        """Test full_name property falls back to username when no names available."""
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
            updated_at=now,
        )

        assert contact.full_name == "john_doe"

    def test_full_name_fallback_to_telegram_id(self):
        """Test full_name property falls back to telegram_id when nothing else available."""
        now = datetime.now()
        contact = Contact(
            id=1,
            telegram_id=123456789,
            username=None,
            first_name=None,
            last_name=None,
            display_name="User 123456789",
            phone=None,
            profile_photo_path=None,
            bio=None,
            created_at=now,
            updated_at=now,
        )

        assert contact.full_name == "User 123456789"

    def test_contact_str_representation(self):
        """Test __str__ method."""
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
            updated_at=now,
        )

        assert str(contact) == "Contact(John Doe, @john_doe)"

    def test_contact_str_without_username(self):
        """Test __str__ method when username is None."""
        now = datetime.now()
        contact = Contact(
            id=1,
            telegram_id=123456789,
            username=None,
            first_name="John",
            last_name="Doe",
            display_name="John Doe",
            phone=None,
            profile_photo_path=None,
            bio=None,
            created_at=now,
            updated_at=now,
        )

        assert str(contact) == "Contact(John Doe, @no_username)"

    def test_contact_repr(self):
        """Test __repr__ method."""
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
            updated_at=now,
        )

        assert repr(contact) == (
            "Contact(id=1, telegram_id=123456789, "
            "username=john_doe, full_name=John Doe)"
        )


class TestGroup:
    """Tests for the Group model."""

    def test_group_creation_with_all_fields(self):
        """Test creating a group with all fields populated."""
        now = datetime.now()
        group = Group(
            id=1,
            telegram_id=987654321,
            name="Python Developers",
            member_count=150,
            profile_photo_path="/path/to/group_photo.jpg",
            created_at=now,
            updated_at=now,
        )

        assert group.id == 1
        assert group.telegram_id == 987654321
        assert group.name == "Python Developers"
        assert group.member_count == 150
        assert group.profile_photo_path == "/path/to/group_photo.jpg"
        assert group.created_at == now
        assert group.updated_at == now

    def test_group_creation_without_photo(self):
        """Test creating a group without a profile photo."""
        now = datetime.now()
        group = Group(
            id=None,
            telegram_id=111222333,
            name="Study Group",
            member_count=25,
            profile_photo_path=None,
            created_at=now,
            updated_at=now,
        )

        assert group.id is None
        assert group.profile_photo_path is None

    def test_group_str_representation(self):
        """Test __str__ method."""
        now = datetime.now()
        group = Group(
            id=1,
            telegram_id=987654321,
            name="Python Developers",
            member_count=150,
            profile_photo_path=None,
            created_at=now,
            updated_at=now,
        )

        assert str(group) == "Group(Python Developers, 150 members)"

    def test_group_repr(self):
        """Test __repr__ method."""
        now = datetime.now()
        group = Group(
            id=1,
            telegram_id=987654321,
            name="Python Developers",
            member_count=150,
            profile_photo_path=None,
            created_at=now,
            updated_at=now,
        )

        assert repr(group) == (
            "Group(id=1, telegram_id=987654321, "
            "name=Python Developers, member_count=150)"
        )


class TestTag:
    """Tests for the Tag model."""

    def test_tag_creation_with_color(self):
        """Test creating a tag with a color."""
        now = datetime.now()
        tag = Tag(
            id=1,
            name="Work",
            color="#FF5733",
            created_at=now,
        )

        assert tag.id == 1
        assert tag.name == "Work"
        assert tag.color == "#FF5733"
        assert tag.created_at == now

    def test_tag_creation_without_color(self):
        """Test creating a tag without a color."""
        now = datetime.now()
        tag = Tag(
            id=None,
            name="Personal",
            color=None,
            created_at=now,
        )

        assert tag.id is None
        assert tag.name == "Personal"
        assert tag.color is None

    def test_tag_str_with_color(self):
        """Test __str__ method with color."""
        now = datetime.now()
        tag = Tag(
            id=1,
            name="Work",
            color="#FF5733",
            created_at=now,
        )

        assert str(tag) == "Tag(Work (#FF5733))"

    def test_tag_str_without_color(self):
        """Test __str__ method without color."""
        now = datetime.now()
        tag = Tag(
            id=1,
            name="Personal",
            color=None,
            created_at=now,
        )

        assert str(tag) == "Tag(Personal)"

    def test_tag_repr(self):
        """Test __repr__ method."""
        now = datetime.now()
        tag = Tag(
            id=1,
            name="Work",
            color="#FF5733",
            created_at=now,
        )

        assert repr(tag) == (f"Tag(id=1, name=Work, color=#FF5733, created_at={now})")

    def test_tag_equality_same_name_case_insensitive(self):
        """Test tag equality with same name (different case)."""
        now = datetime.now()
        tag1 = Tag(id=1, name="Work", color="#FF5733", created_at=now)
        tag2 = Tag(id=2, name="work", color="#00FF00", created_at=now)

        assert tag1 == tag2

    def test_tag_equality_different_names(self):
        """Test tag inequality with different names."""
        now = datetime.now()
        tag1 = Tag(id=1, name="Work", color="#FF5733", created_at=now)
        tag2 = Tag(id=2, name="Personal", color="#FF5733", created_at=now)

        assert tag1 != tag2

    def test_tag_equality_with_non_tag(self):
        """Test tag equality with non-Tag object."""
        now = datetime.now()
        tag = Tag(id=1, name="Work", color="#FF5733", created_at=now)

        assert tag != "Work"
        assert tag != 1
        assert tag != None

    def test_tag_hash(self):
        """Test tag hashing for use in sets and dicts."""
        now = datetime.now()
        tag1 = Tag(id=1, name="Work", color="#FF5733", created_at=now)
        tag2 = Tag(id=2, name="work", color="#00FF00", created_at=now)
        tag3 = Tag(id=3, name="Personal", color="#FF5733", created_at=now)

        # Same name (different case) should have same hash
        assert hash(tag1) == hash(tag2)

        # Different names should (likely) have different hash
        assert hash(tag1) != hash(tag3)

    def test_tag_in_set(self):
        """Test that tags can be used in sets correctly."""
        now = datetime.now()
        tag1 = Tag(id=1, name="Work", color="#FF5733", created_at=now)
        tag2 = Tag(id=2, name="work", color="#00FF00", created_at=now)
        tag3 = Tag(id=3, name="Personal", color="#FF5733", created_at=now)

        tag_set = {tag1, tag2, tag3}

        # tag1 and tag2 are considered equal, so only 2 unique tags
        assert len(tag_set) == 2


class TestMessage:
    """Tests for the Message model."""

    def test_outgoing_message_creation(self):
        """Test creating an outgoing message."""
        now = datetime.now()
        message = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=10,
            is_outgoing=True,
            content="Hello, how are you?",
            timestamp=now,
            created_at=now,
        )

        assert message.id == 1
        assert message.telegram_message_id == 12345
        assert message.contact_id == 10
        assert message.is_outgoing is True
        assert message.content == "Hello, how are you?"
        assert message.timestamp == now
        assert message.created_at == now

    def test_incoming_message_creation(self):
        """Test creating an incoming message."""
        now = datetime.now()
        message = Message(
            id=2,
            telegram_message_id=12346,
            contact_id=10,
            is_outgoing=False,
            content="I'm doing great, thanks!",
            timestamp=now,
            created_at=now,
        )

        assert message.is_outgoing is False

    def test_message_without_content(self):
        """Test creating a message without content (media only)."""
        now = datetime.now()
        message = Message(
            id=3,
            telegram_message_id=12347,
            contact_id=10,
            is_outgoing=True,
            content=None,
            timestamp=now,
            created_at=now,
        )

        assert message.content is None

    def test_message_without_telegram_id(self):
        """Test creating a message without telegram_message_id."""
        now = datetime.now()
        message = Message(
            id=None,
            telegram_message_id=None,
            contact_id=10,
            is_outgoing=True,
            content="Test message",
            timestamp=now,
            created_at=now,
        )

        assert message.telegram_message_id is None

    def test_direction_property_outgoing(self):
        """Test direction property for outgoing message."""
        now = datetime.now()
        message = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=10,
            is_outgoing=True,
            content="Test",
            timestamp=now,
            created_at=now,
        )

        assert message.direction == "sent"

    def test_direction_property_incoming(self):
        """Test direction property for incoming message."""
        now = datetime.now()
        message = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=10,
            is_outgoing=False,
            content="Test",
            timestamp=now,
            created_at=now,
        )

        assert message.direction == "received"

    def test_preview_short_content(self):
        """Test preview property with short content."""
        now = datetime.now()
        message = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=10,
            is_outgoing=True,
            content="Hello!",
            timestamp=now,
            created_at=now,
        )

        assert message.preview == "Hello!"

    def test_preview_long_content(self):
        """Test preview property with long content (truncation)."""
        now = datetime.now()
        long_content = "A" * 150  # 150 character string
        message = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=10,
            is_outgoing=True,
            content=long_content,
            timestamp=now,
            created_at=now,
        )

        assert len(message.preview) == 103  # 100 chars + "..."
        assert message.preview.endswith("...")
        assert message.preview == long_content[:100] + "..."

    def test_preview_no_content(self):
        """Test preview property when content is None."""
        now = datetime.now()
        message = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=10,
            is_outgoing=True,
            content=None,
            timestamp=now,
            created_at=now,
        )

        assert message.preview == "[No content]"

    def test_preview_empty_content(self):
        """Test preview property when content is empty string."""
        now = datetime.now()
        message = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=10,
            is_outgoing=True,
            content="",
            timestamp=now,
            created_at=now,
        )

        assert message.preview == "[No content]"

    def test_message_str_outgoing(self):
        """Test __str__ method for outgoing message."""
        now = datetime.now()
        message = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=10,
            is_outgoing=True,
            content="Hello, how are you?",
            timestamp=now,
            created_at=now,
        )

        assert str(message) == "Message(→ Hello, how are you?)"

    def test_message_str_incoming(self):
        """Test __str__ method for incoming message."""
        now = datetime.now()
        message = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=10,
            is_outgoing=False,
            content="I'm doing great!",
            timestamp=now,
            created_at=now,
        )

        assert str(message) == "Message(← I'm doing great!)"

    def test_message_repr(self):
        """Test __repr__ method."""
        now = datetime.now()
        message = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=10,
            is_outgoing=True,
            content="Test",
            timestamp=now,
            created_at=now,
        )

        assert repr(message) == (
            f"Message(id=1, telegram_message_id=12345, "
            f"contact_id=10, is_outgoing=True, timestamp={now})"
        )


class TestContactProfile:
    """Tests for the ContactProfile model."""

    def test_contact_profile_creation(self):
        """Test creating a complete contact profile."""
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
            updated_at=now,
        )

        tag1 = Tag(id=1, name="Work", color="#FF5733", created_at=now)
        tag2 = Tag(id=2, name="Friend", color="#00FF00", created_at=now)

        group1 = Group(
            id=1,
            telegram_id=111,
            name="Python Devs",
            member_count=100,
            profile_photo_path=None,
            created_at=now,
            updated_at=now,
        )

        last_received = Message(
            id=1,
            telegram_message_id=12345,
            contact_id=1,
            is_outgoing=False,
            content="Hey there!",
            timestamp=now,
            created_at=now,
        )

        last_sent = Message(
            id=2,
            telegram_message_id=12346,
            contact_id=1,
            is_outgoing=True,
            content="Hi! How are you?",
            timestamp=now,
            created_at=now,
        )

        profile = ContactProfile(
            contact=contact,
            tags=[tag1, tag2],
            mutual_groups=[group1],
            last_received_message=last_received,
            last_sent_message=last_sent,
        )

        assert profile.contact == contact
        assert len(profile.tags) == 2
        assert tag1 in profile.tags
        assert tag2 in profile.tags
        assert len(profile.mutual_groups) == 1
        assert profile.mutual_groups[0] == group1
        assert profile.last_received_message == last_received
        assert profile.last_sent_message == last_sent

    def test_contact_profile_with_no_tags(self):
        """Test contact profile with empty tags list."""
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
            updated_at=now,
        )

        profile = ContactProfile(
            contact=contact,
            tags=[],
            mutual_groups=[],
            last_received_message=None,
            last_sent_message=None,
        )

        assert len(profile.tags) == 0
        assert len(profile.mutual_groups) == 0
        assert profile.last_received_message is None
        assert profile.last_sent_message is None

    def test_contact_profile_str(self):
        """Test __str__ method."""
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
            updated_at=now,
        )

        tag1 = Tag(id=1, name="Work", color="#FF5733", created_at=now)
        tag2 = Tag(id=2, name="Friend", color="#00FF00", created_at=now)

        group1 = Group(
            id=1,
            telegram_id=111,
            name="Python Devs",
            member_count=100,
            profile_photo_path=None,
            created_at=now,
            updated_at=now,
        )

        profile = ContactProfile(
            contact=contact,
            tags=[tag1, tag2],
            mutual_groups=[group1],
            last_received_message=None,
            last_sent_message=None,
        )

        assert str(profile) == "ContactProfile(John Doe, 2 tags, 1 mutual groups)"

    def test_contact_profile_with_multiple_groups(self):
        """Test contact profile with multiple mutual groups."""
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
            updated_at=now,
        )

        group1 = Group(
            id=1,
            telegram_id=111,
            name="Python Devs",
            member_count=100,
            profile_photo_path=None,
            created_at=now,
            updated_at=now,
        )

        group2 = Group(
            id=2,
            telegram_id=222,
            name="Tech Enthusiasts",
            member_count=200,
            profile_photo_path=None,
            created_at=now,
            updated_at=now,
        )

        group3 = Group(
            id=3,
            telegram_id=333,
            name="Book Club",
            member_count=50,
            profile_photo_path=None,
            created_at=now,
            updated_at=now,
        )

        profile = ContactProfile(
            contact=contact,
            tags=[],
            mutual_groups=[group1, group2, group3],
            last_received_message=None,
            last_sent_message=None,
        )

        assert len(profile.mutual_groups) == 3
        assert str(profile) == "ContactProfile(John Doe, 0 tags, 3 mutual groups)"

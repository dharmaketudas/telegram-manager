"""
Unit tests for TagRepository

Tests all CRUD operations and many-to-many relationship management
for tags and contact-tag associations.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models.tag import Tag, contact_tags
from src.models.contact import Contact
from src.database.base import Base
from src.repositories.tag_repository import TagRepository


# Fixtures


@pytest.fixture
async def async_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def async_session(async_engine):
    """Create a new database session for each test."""
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def tag_repository(async_session):
    """Create a TagRepository instance."""
    return TagRepository(async_session)


@pytest.fixture
async def sample_contact(async_session):
    """Create a sample contact for testing."""
    contact = Contact(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User",
        display_name="Test User",
        phone="+1234567890",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(contact)
    await async_session.commit()
    await async_session.refresh(contact)
    return contact


@pytest.fixture
async def sample_tag(tag_repository):
    """Create a sample tag for testing."""
    tag_data = {"name": "Friends", "color": "#FF5733"}
    return await tag_repository.create(tag_data)


# Test Cases


class TestTagRepositoryCreate:
    """Tests for tag creation."""

    @pytest.mark.asyncio
    async def test_create_tag_with_color(self, tag_repository):
        """Test creating a tag with a color."""
        tag_data = {"name": "Work", "color": "#3498DB"}

        tag = await tag_repository.create(tag_data)

        assert tag.id is not None
        assert tag.name == "Work"
        assert tag.color == "#3498DB"
        assert isinstance(tag.created_at, datetime)

    @pytest.mark.asyncio
    async def test_create_tag_without_color(self, tag_repository):
        """Test creating a tag without a color."""
        tag_data = {"name": "Family"}

        tag = await tag_repository.create(tag_data)

        assert tag.id is not None
        assert tag.name == "Family"
        assert tag.color is None
        assert isinstance(tag.created_at, datetime)

    @pytest.mark.asyncio
    async def test_create_tag_duplicate_name_fails(self, tag_repository):
        """Test that creating a tag with duplicate name fails."""
        tag_data = {"name": "Colleagues", "color": "#FF0000"}
        await tag_repository.create(tag_data)

        # Try to create another tag with the same name
        with pytest.raises(ValueError, match="already exists"):
            await tag_repository.create(tag_data)

    @pytest.mark.asyncio
    async def test_create_tag_sets_timestamp(self, tag_repository):
        """Test that created_at is set automatically."""
        tag_data = {"name": "Important"}

        before = datetime.utcnow()
        tag = await tag_repository.create(tag_data)
        after = datetime.utcnow()

        assert before <= tag.created_at <= after


class TestTagRepositoryRead:
    """Tests for tag retrieval."""

    @pytest.mark.asyncio
    async def test_get_by_id_existing(self, tag_repository, sample_tag):
        """Test retrieving an existing tag by ID."""
        tag = await tag_repository.get_by_id(sample_tag.id)

        assert tag is not None
        assert tag.id == sample_tag.id
        assert tag.name == sample_tag.name
        assert tag.color == sample_tag.color

    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent(self, tag_repository):
        """Test retrieving a non-existent tag returns None."""
        tag = await tag_repository.get_by_id(99999)

        assert tag is None

    @pytest.mark.asyncio
    async def test_get_by_name_existing(self, tag_repository, sample_tag):
        """Test retrieving an existing tag by name."""
        tag = await tag_repository.get_by_name("Friends")

        assert tag is not None
        assert tag.name == "Friends"
        assert tag.color == "#FF5733"

    @pytest.mark.asyncio
    async def test_get_by_name_case_insensitive(self, tag_repository, sample_tag):
        """Test that name search is case-insensitive."""
        tag = await tag_repository.get_by_name("fRiEnDs")

        assert tag is not None
        assert tag.name == "Friends"

    @pytest.mark.asyncio
    async def test_get_by_name_nonexistent(self, tag_repository):
        """Test retrieving a non-existent tag by name returns None."""
        tag = await tag_repository.get_by_name("NonExistent")

        assert tag is None

    @pytest.mark.asyncio
    async def test_get_all_empty(self, tag_repository):
        """Test getting all tags when none exist."""
        tags = await tag_repository.get_all()

        assert tags == []

    @pytest.mark.asyncio
    async def test_get_all_multiple_tags(self, tag_repository):
        """Test getting all tags."""
        # Create multiple tags
        await tag_repository.create({"name": "Work", "color": "#FF0000"})
        await tag_repository.create({"name": "Personal", "color": "#00FF00"})
        await tag_repository.create({"name": "Urgent", "color": "#0000FF"})

        tags = await tag_repository.get_all()

        assert len(tags) == 3
        # Verify ordering by name
        tag_names = [tag.name for tag in tags]
        assert tag_names == sorted(tag_names)

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, tag_repository):
        """Test getting all tags with pagination."""
        # Create multiple tags
        for i in range(10):
            await tag_repository.create({"name": f"Tag{i:02d}"})

        # Get first 5
        tags_page1 = await tag_repository.get_all(limit=5, offset=0)
        assert len(tags_page1) == 5

        # Get next 5
        tags_page2 = await tag_repository.get_all(limit=5, offset=5)
        assert len(tags_page2) == 5

        # Ensure no overlap
        page1_ids = {tag.id for tag in tags_page1}
        page2_ids = {tag.id for tag in tags_page2}
        assert len(page1_ids & page2_ids) == 0


class TestTagRepositoryUpdate:
    """Tests for tag updates."""

    @pytest.mark.asyncio
    async def test_update_tag_name(self, tag_repository, sample_tag):
        """Test updating a tag's name."""
        updated_tag = await tag_repository.update(
            sample_tag.id, {"name": "Best Friends"}
        )

        assert updated_tag is not None
        assert updated_tag.id == sample_tag.id
        assert updated_tag.name == "Best Friends"
        assert updated_tag.color == sample_tag.color

    @pytest.mark.asyncio
    async def test_update_tag_color(self, tag_repository, sample_tag):
        """Test updating a tag's color."""
        updated_tag = await tag_repository.update(sample_tag.id, {"color": "#00FF00"})

        assert updated_tag is not None
        assert updated_tag.name == sample_tag.name
        assert updated_tag.color == "#00FF00"

    @pytest.mark.asyncio
    async def test_update_nonexistent_tag(self, tag_repository):
        """Test updating a non-existent tag returns None."""
        updated_tag = await tag_repository.update(99999, {"name": "New Name"})

        assert updated_tag is None

    @pytest.mark.asyncio
    async def test_update_to_duplicate_name_fails(self, tag_repository):
        """Test that updating to a duplicate name fails."""
        tag1 = await tag_repository.create({"name": "Tag1"})
        tag2 = await tag_repository.create({"name": "Tag2"})

        with pytest.raises(ValueError, match="already exists"):
            await tag_repository.update(tag2.id, {"name": "Tag1"})


class TestTagRepositoryDelete:
    """Tests for tag deletion."""

    @pytest.mark.asyncio
    async def test_delete_existing_tag(self, tag_repository, sample_tag):
        """Test deleting an existing tag."""
        result = await tag_repository.delete(sample_tag.id)

        assert result is True

        # Verify tag is deleted
        tag = await tag_repository.get_by_id(sample_tag.id)
        assert tag is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tag(self, tag_repository):
        """Test deleting a non-existent tag returns False."""
        result = await tag_repository.delete(99999)

        assert result is False


class TestTagRepositoryAssociations:
    """Tests for contact-tag association management."""

    @pytest.mark.asyncio
    async def test_add_tag_to_contact(self, tag_repository, sample_contact, sample_tag):
        """Test adding a tag to a contact."""
        result = await tag_repository.add_tag_to_contact(
            sample_contact.id, sample_tag.id
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_add_tag_to_contact_duplicate(
        self, tag_repository, sample_contact, sample_tag
    ):
        """Test adding the same tag twice returns False."""
        await tag_repository.add_tag_to_contact(sample_contact.id, sample_tag.id)
        result = await tag_repository.add_tag_to_contact(
            sample_contact.id, sample_tag.id
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_add_tag_to_nonexistent_contact(self, tag_repository, sample_tag):
        """Test adding a tag to non-existent contact raises error."""
        with pytest.raises(ValueError, match="Contact.*not found"):
            await tag_repository.add_tag_to_contact(99999, sample_tag.id)

    @pytest.mark.asyncio
    async def test_add_nonexistent_tag_to_contact(self, tag_repository, sample_contact):
        """Test adding a non-existent tag raises error."""
        with pytest.raises(ValueError, match="Tag.*not found"):
            await tag_repository.add_tag_to_contact(sample_contact.id, 99999)

    @pytest.mark.asyncio
    async def test_remove_tag_from_contact(
        self, tag_repository, sample_contact, sample_tag
    ):
        """Test removing a tag from a contact."""
        # First add the tag
        await tag_repository.add_tag_to_contact(sample_contact.id, sample_tag.id)

        # Then remove it
        result = await tag_repository.remove_tag_from_contact(
            sample_contact.id, sample_tag.id
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_remove_nonexistent_association(
        self, tag_repository, sample_contact, sample_tag
    ):
        """Test removing a non-existent association returns False."""
        result = await tag_repository.remove_tag_from_contact(
            sample_contact.id, sample_tag.id
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_get_tags_for_contact_empty(self, tag_repository, sample_contact):
        """Test getting tags for a contact with no tags."""
        tags = await tag_repository.get_tags_for_contact(sample_contact.id)

        assert tags == []

    @pytest.mark.asyncio
    async def test_get_tags_for_contact_multiple(self, tag_repository, sample_contact):
        """Test getting multiple tags for a contact."""
        # Create and add multiple tags
        tag1 = await tag_repository.create({"name": "Work", "color": "#FF0000"})
        tag2 = await tag_repository.create({"name": "Personal", "color": "#00FF00"})
        tag3 = await tag_repository.create({"name": "Urgent", "color": "#0000FF"})

        await tag_repository.add_tag_to_contact(sample_contact.id, tag1.id)
        await tag_repository.add_tag_to_contact(sample_contact.id, tag2.id)
        await tag_repository.add_tag_to_contact(sample_contact.id, tag3.id)

        tags = await tag_repository.get_tags_for_contact(sample_contact.id)

        assert len(tags) == 3
        tag_names = {tag.name for tag in tags}
        assert tag_names == {"Work", "Personal", "Urgent"}

    @pytest.mark.asyncio
    async def test_get_contacts_by_tag_empty(self, tag_repository, sample_tag):
        """Test getting contacts for a tag with no contacts."""
        contacts = await tag_repository.get_contacts_by_tag(sample_tag.id)

        assert contacts == []

    @pytest.mark.asyncio
    async def test_get_contacts_by_tag_multiple(self, tag_repository, async_session):
        """Test getting multiple contacts for a tag."""
        # Create multiple contacts
        contact1 = Contact(
            telegram_id=111,
            display_name="Contact 1",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        contact2 = Contact(
            telegram_id=222,
            display_name="Contact 2",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        contact3 = Contact(
            telegram_id=333,
            display_name="Contact 3",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        async_session.add_all([contact1, contact2, contact3])
        await async_session.commit()
        await async_session.refresh(contact1)
        await async_session.refresh(contact2)
        await async_session.refresh(contact3)

        # Create a tag and associate with contacts
        tag = await tag_repository.create({"name": "VIP", "color": "#FFD700"})
        await tag_repository.add_tag_to_contact(contact1.id, tag.id)
        await tag_repository.add_tag_to_contact(contact2.id, tag.id)
        await tag_repository.add_tag_to_contact(contact3.id, tag.id)

        contacts = await tag_repository.get_contacts_by_tag(tag.id)

        assert len(contacts) == 3
        contact_ids = {c.id for c in contacts}
        assert contact_ids == {contact1.id, contact2.id, contact3.id}

    @pytest.mark.asyncio
    async def test_get_contacts_by_tags_empty_list(self, tag_repository):
        """Test getting contacts with empty tag list."""
        contacts = await tag_repository.get_contacts_by_tags([])

        assert contacts == []

    @pytest.mark.asyncio
    async def test_get_contacts_by_tags_multiple(self, tag_repository, async_session):
        """Test getting contacts that have any of multiple tags."""
        # Create contacts
        contact1 = Contact(
            telegram_id=111,
            display_name="Contact 1",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        contact2 = Contact(
            telegram_id=222,
            display_name="Contact 2",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        contact3 = Contact(
            telegram_id=333,
            display_name="Contact 3",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        async_session.add_all([contact1, contact2, contact3])
        await async_session.commit()
        await async_session.refresh(contact1)
        await async_session.refresh(contact2)
        await async_session.refresh(contact3)

        # Create tags
        tag1 = await tag_repository.create({"name": "Work"})
        tag2 = await tag_repository.create({"name": "Personal"})

        # Associate: contact1 has tag1, contact2 has tag2, contact3 has both
        await tag_repository.add_tag_to_contact(contact1.id, tag1.id)
        await tag_repository.add_tag_to_contact(contact2.id, tag2.id)
        await tag_repository.add_tag_to_contact(contact3.id, tag1.id)
        await tag_repository.add_tag_to_contact(contact3.id, tag2.id)

        # Get contacts with either tag1 or tag2
        contacts = await tag_repository.get_contacts_by_tags([tag1.id, tag2.id])

        assert len(contacts) == 3
        contact_ids = {c.id for c in contacts}
        assert contact_ids == {contact1.id, contact2.id, contact3.id}


class TestTagRepositoryCounts:
    """Tests for counting associations."""

    @pytest.mark.asyncio
    async def test_get_tag_count_for_contact_zero(self, tag_repository, sample_contact):
        """Test getting tag count for contact with no tags."""
        count = await tag_repository.get_tag_count_for_contact(sample_contact.id)

        assert count == 0

    @pytest.mark.asyncio
    async def test_get_tag_count_for_contact_multiple(
        self, tag_repository, sample_contact
    ):
        """Test getting tag count for contact with multiple tags."""
        tag1 = await tag_repository.create({"name": "Tag1"})
        tag2 = await tag_repository.create({"name": "Tag2"})
        tag3 = await tag_repository.create({"name": "Tag3"})

        await tag_repository.add_tag_to_contact(sample_contact.id, tag1.id)
        await tag_repository.add_tag_to_contact(sample_contact.id, tag2.id)
        await tag_repository.add_tag_to_contact(sample_contact.id, tag3.id)

        count = await tag_repository.get_tag_count_for_contact(sample_contact.id)

        assert count == 3

    @pytest.mark.asyncio
    async def test_get_contact_count_for_tag_zero(self, tag_repository, sample_tag):
        """Test getting contact count for tag with no contacts."""
        count = await tag_repository.get_contact_count_for_tag(sample_tag.id)

        assert count == 0

    @pytest.mark.asyncio
    async def test_get_contact_count_for_tag_multiple(
        self, tag_repository, async_session
    ):
        """Test getting contact count for tag with multiple contacts."""
        # Create contacts
        contacts = []
        for i in range(5):
            contact = Contact(
                telegram_id=1000 + i,
                display_name=f"Contact {i}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            contacts.append(contact)

        async_session.add_all(contacts)
        await async_session.commit()

        for contact in contacts:
            await async_session.refresh(contact)

        # Create tag and associate with all contacts
        tag = await tag_repository.create({"name": "Popular"})
        for contact in contacts:
            await tag_repository.add_tag_to_contact(contact.id, tag.id)

        count = await tag_repository.get_contact_count_for_tag(tag.id)

        assert count == 5


class TestTagRepositoryHelpers:
    """Tests for helper methods."""

    @pytest.mark.asyncio
    async def test_exists_by_name_true(self, tag_repository, sample_tag):
        """Test that exists_by_name returns True for existing tag."""
        exists = await tag_repository.exists_by_name("Friends")

        assert exists is True

    @pytest.mark.asyncio
    async def test_exists_by_name_false(self, tag_repository):
        """Test that exists_by_name returns False for non-existent tag."""
        exists = await tag_repository.exists_by_name("NonExistent")

        assert exists is False

    @pytest.mark.asyncio
    async def test_exists_by_name_case_insensitive(self, tag_repository, sample_tag):
        """Test that exists_by_name is case-insensitive."""
        exists = await tag_repository.exists_by_name("fRiEnDs")

        assert exists is True


class TestTagRepositoryCascadeDelete:
    """Tests for cascade deletion behavior."""

    @pytest.mark.asyncio
    async def test_delete_tag_removes_associations(
        self, tag_repository, sample_contact, sample_tag
    ):
        """Test that deleting a tag removes all contact associations."""
        # Add tag to contact
        await tag_repository.add_tag_to_contact(sample_contact.id, sample_tag.id)

        # Verify association exists
        tags = await tag_repository.get_tags_for_contact(sample_contact.id)
        assert len(tags) == 1

        # Delete the tag
        await tag_repository.delete(sample_tag.id)

        # Verify associations are removed
        tags = await tag_repository.get_tags_for_contact(sample_contact.id)
        assert len(tags) == 0

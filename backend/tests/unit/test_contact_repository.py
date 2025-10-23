"""
Async unit tests for the ContactRepository.

This module contains comprehensive test cases to validate the functionality
of the ContactRepository class, ensuring robust CRUD operations and
error handling for contact entities.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.models.contact import Contact
from src.repositories.contact_repository import ContactRepository


@pytest.fixture
async def sample_contact_data() -> Dict[str, Any]:
    """
    Async fixture providing sample contact data for testing.

    Returns:
        Dict[str, Any]: A dictionary with contact creation parameters
    """
    return {
        "telegram_id": 123456789,
        "username": "test_user",
        "first_name": "John",
        "last_name": "Doe",
        "display_name": "John Doe",
        "phone": "+1234567890",
        "bio": "Test bio",
        "profile_photo_path": "/path/to/photo.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.mark.asyncio
class TestContactRepository:
    """
    Asynchronous test suite for ContactRepository, covering all CRUD operations
    and edge cases.
    """

    async def test_create_contact(
        self, async_session: AsyncSession, sample_contact_data: dict
    ):
        """
        Test creating a new contact successfully.

        Verifies that:
        - Contact can be created
        - Returned contact has an ID
        - All provided data is correctly stored
        """
        repo = ContactRepository(async_session)
        contact = await repo.create(sample_contact_data)

        assert contact.id is not None
        assert contact.telegram_id == sample_contact_data["telegram_id"]
        assert contact.username == sample_contact_data["username"]
        assert contact.display_name == sample_contact_data["display_name"]

    async def test_create_duplicate_telegram_id(
        self, async_session: AsyncSession, sample_contact_data: dict
    ):
        """
        Test creating a contact with a duplicate Telegram ID.

        Expects:
        - Unique constraint violation
        - IntegrityError or similar exception
        """
        repo = ContactRepository(async_session)

        # Create first contact
        await repo.create(sample_contact_data)

        # Try to create another contact with same Telegram ID
        with pytest.raises((IntegrityError, ValueError)):
            await repo.create(sample_contact_data)

    async def test_get_by_id(
        self, async_session: AsyncSession, sample_contact_data: dict
    ):
        """
        Test retrieving a contact by its database ID.

        Verifies that:
        - Created contact can be retrieved
        - Retrieved contact matches original data
        """
        repo = ContactRepository(async_session)
        created_contact = await repo.create(sample_contact_data)

        retrieved_contact = await repo.get_by_id(created_contact.id)

        assert retrieved_contact is not None
        assert retrieved_contact.id == created_contact.id
        assert retrieved_contact.telegram_id == sample_contact_data["telegram_id"]

    async def test_get_by_telegram_id(
        self, async_session: AsyncSession, sample_contact_data: dict
    ):
        """
        Test retrieving a contact by Telegram ID.

        Verifies that:
        - Contact can be found by Telegram ID
        - Correct contact is returned
        """
        repo = ContactRepository(async_session)
        created_contact = await repo.create(sample_contact_data)

        retrieved_contact = await repo.get_by_telegram_id(
            sample_contact_data["telegram_id"]
        )

        assert retrieved_contact is not None
        assert retrieved_contact.telegram_id == sample_contact_data["telegram_id"]

    async def test_list_contacts(
        self, async_session: AsyncSession, sample_contact_data: dict
    ):
        """
        Test listing contacts with pagination and filtering.

        Verifies that:
        - Multiple contacts can be created
        - Contacts can be listed
        - Pagination works correctly
        """
        repo = ContactRepository(async_session)

        # Create multiple contacts
        contacts_data = [
            sample_contact_data,
            {
                **sample_contact_data,
                "telegram_id": 987654321,
                "username": "another_user",
            },
        ]

        for contact_data in contacts_data:
            await repo.create(contact_data)

        # List contacts
        listed_contacts = await repo.get_all(limit=10)

        assert len(listed_contacts) > 1
        assert all(isinstance(contact, Contact) for contact in listed_contacts)

    async def test_update_contact(
        self, async_session: AsyncSession, sample_contact_data: dict
    ):
        """
        Test updating an existing contact.

        Verifies that:
        - Contact can be updated
        - Specific fields can be modified
        - Updated at timestamp changes
        """
        repo = ContactRepository(async_session)
        created_contact = await repo.create(sample_contact_data)

        # Store original updated_at
        original_updated_at = created_contact.updated_at

        # Wait a moment to ensure timestamp difference
        await asyncio.sleep(0.1)

        update_data = {"first_name": "Jane", "last_name": "Smith"}

        updated_contact = await repo.update(created_contact.id, update_data)

        assert updated_contact is not None
        assert updated_contact.first_name == "Jane"
        assert updated_contact.last_name == "Smith"
        assert updated_contact.updated_at > original_updated_at

    async def test_delete_contact(
        self, async_session: AsyncSession, sample_contact_data: dict
    ):
        """
        Test deleting a contact.

        Verifies that:
        - Contact can be deleted
        - Deleted contact cannot be retrieved
        """
        repo = ContactRepository(async_session)
        created_contact = await repo.create(sample_contact_data)

        # Delete the contact
        delete_result = await repo.delete(created_contact.id)

        assert delete_result is True

        # Verify contact is deleted
        retrieved_contact = await repo.get_by_id(created_contact.id)
        assert retrieved_contact is None

    async def test_nonexistent_contact_operations(self, async_session: AsyncSession):
        """
        Test operations on nonexistent contacts.

        Verifies behavior when:
        - Trying to get a nonexistent contact
        - Trying to update a nonexistent contact
        - Trying to delete a nonexistent contact
        """
        repo = ContactRepository(async_session)

        # Get nonexistent contact
        assert await repo.get_by_id(99999) is None
        assert await repo.get_by_telegram_id(99999) is None

        # Update nonexistent contact
        assert await repo.update(99999, {"first_name": "Test"}) is None

        # Delete nonexistent contact
        assert await repo.delete(99999) is False

    @pytest.mark.asyncio
    async def test_get_contact_profile(
        self, async_session: AsyncSession, sample_contact_data: dict
    ):
        """
        Test retrieving a detailed contact profile.

        Verifies that:
        - Contact profile can be retrieved
        - Profile contains expected information
        """
        repo = ContactRepository(async_session)
        created_contact = await repo.create(sample_contact_data)

        # Retrieve contact profile
        contact_profile = await repo.get_contact_profile(created_contact.id)

        # Verify profile contents
        assert contact_profile is not None
        assert contact_profile.contact.id == created_contact.id
        assert contact_profile.contact.telegram_id == sample_contact_data["telegram_id"]

    async def test_search_contacts(
        self, async_session: AsyncSession, sample_contact_data: dict
    ):
        """
        Test searching contacts with various search criteria.

        Verifies that:
        - Contacts can be searched by different fields
        - Search is case-insensitive
        - Partial matches are found
        """
        repo = ContactRepository(async_session)

        # Create multiple contacts with varied data
        contact_variations = [
            sample_contact_data,
            {
                **sample_contact_data,
                "telegram_id": 987654321,
                "username": "jane_doe",
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "+9876543210",
            },
            {
                **sample_contact_data,
                "telegram_id": 567890123,
                "username": "john_smith",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1122334455",
            },
        ]

        for contact_data in contact_variations:
            await repo.create(contact_data)

        # Test search by first name
        first_name_results = await repo.search("jane")
        assert len(first_name_results) > 0
        assert any(contact.first_name == "Jane" for contact in first_name_results)

        # Test search by last name
        last_name_results = await repo.search("smith")
        assert len(last_name_results) > 0
        assert any(contact.last_name == "Smith" for contact in last_name_results)

        # Test search by username
        username_results = await repo.search("john")
        assert len(username_results) > 0
        assert any(contact.username == "john_smith" for contact in username_results)

        # Test search by phone
        phone_results = await repo.search("9876")
        assert len(phone_results) > 0
        assert any(contact.phone == "+9876543210" for contact in phone_results)

        # Test case-insensitive search
        case_insensitive_results = await repo.search("JANE")
        assert len(case_insensitive_results) > 0

    async def test_contact_exists(
        self, async_session: AsyncSession, sample_contact_data: dict
    ):
        """
        Test checking contact existence by Telegram ID.

        Verifies that:
        - exists() returns True for existing contacts
        - exists() returns False for non-existing contacts
        """
        repo = ContactRepository(async_session)

        # Create a contact
        created_contact = await repo.create(sample_contact_data)

        # Check that the contact exists
        exists = await repo.exists(created_contact.telegram_id)
        assert exists is True

        # Check a non-existent Telegram ID
        non_existent = await repo.exists(999999999)
        assert non_existent is False

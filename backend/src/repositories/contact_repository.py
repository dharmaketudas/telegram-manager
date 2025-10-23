"""
Async Contact Repository for managing contact entities.

Provides asynchronous CRUD operations for contacts using SQLAlchemy.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.contact import Contact
from src.schemas.contact import ContactResponse, ContactProfileResponse


class ContactRepository:
    """
    Asynchronous repository for Contact entities with comprehensive operations.

    Provides methods for creating, reading, updating, and deleting
    contacts with robust error handling.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with an async database session.

        Args:
            session (AsyncSession): Async SQLAlchemy database session
        """
        self.session = session

    async def create(self, contact_data: Dict[str, Any]) -> Contact:
        """
        Asynchronously create a new contact.

        Args:
            contact_data (Dict[str, Any]): Data for creating a new contact

        Returns:
            Contact: The newly created contact
        """
        try:
            # Set default timestamps if not provided
            # Set default timestamps if not provided
            contact_data.setdefault("created_at", datetime.utcnow())
            contact_data.setdefault("updated_at", datetime.utcnow())

            # Remove id if None to allow SQLAlchemy to generate
            if "id" in contact_data and contact_data["id"] is None:
                del contact_data["id"]

            contact = Contact(id=None, **contact_data)
            self.session.add(contact)
            await self.session.commit()
            await self.session.refresh(contact)
            return contact
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to create contact: {str(e)}") from e

    async def get_by_id(self, contact_id: int) -> Optional[Contact]:
        """
        Retrieve a contact by its database ID.

        Args:
            contact_id (int): The unique database ID of the contact

        Returns:
            Optional[Contact]: The contact if found, None otherwise
        """
        return await self.session.get(Contact, contact_id)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Contact]:
        """
        Retrieve a contact by its Telegram user ID.

        Args:
            telegram_id (int): The Telegram user ID

        Returns:
            Optional[Contact]: The contact if found, None otherwise
        """
        query = select(Contact).where(Contact.telegram_id == telegram_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Contact]:
        """
        Retrieve all contacts with optional pagination.

        Args:
            limit (Optional[int]): Maximum number of records to return
            offset (int): Number of records to skip

        Returns:
            List[Contact]: List of contacts
        """
        query = select(Contact)

        if limit is not None:
            query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self, contact_id: int, update_data: Dict[str, Any]
    ) -> Optional[Contact]:
        """
        Update an existing contact.

        Args:
            contact_id (int): ID of the contact to update
            update_data (Dict[str, Any]): Fields to update

        Returns:
            Optional[Contact]: Updated contact, or None if not found
        """
        try:
            # Fetch the existing contact
            contact = await self.get_by_id(contact_id)
            if not contact:
                return None

            # Update timestamps and fields
            update_data["updated_at"] = datetime.utcnow()

            for key, value in update_data.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)

            await self.session.commit()
            await self.session.refresh(contact)
            return contact

        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to update contact: {str(e)}") from e

    async def delete(self, contact_id: int) -> bool:
        """
        Delete a contact by its database ID.

        Args:
            contact_id (int): ID of the contact to delete

        Returns:
            bool: True if contact was deleted, False if not found
        """
        try:
            contact = await self.get_by_id(contact_id)
            if not contact:
                return False

            await self.session.delete(contact)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False

    async def search(
        self, query: str, limit: int = 50, offset: int = 0
    ) -> List[Contact]:
        """
        Search contacts by a query string across multiple fields.

        Args:
            query (str): Search term to match against contact fields
            limit (int): Maximum number of results to return
            offset (int): Number of results to skip

        Returns:
            List[Contact]: List of contacts matching the search query
        """
        if not query or len(query.strip()) < 2:
            return []

        search_query = f"%{query.lower()}%"

        stmt = (
            select(Contact)
            .where(
                (Contact.username.ilike(search_query))
                | (Contact.first_name.ilike(search_query))
                | (Contact.last_name.ilike(search_query))
                | (Contact.display_name.ilike(search_query))
                | (Contact.phone.ilike(search_query))
                | (Contact.bio.ilike(search_query))
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists(self, telegram_id: int) -> bool:
        """
        Check if a contact exists with the given Telegram ID.

        Args:
            telegram_id (int): Telegram user ID to check

        Returns:
            bool: True if contact exists, False otherwise
        """
        query = select(Contact).where(Contact.telegram_id == telegram_id)
        result = await self.session.execute(query)
        return result.first() is not None

    async def get_contact_profile(
        self, contact_id: int
    ) -> Optional[ContactProfileResponse]:
        """
        Retrieve a detailed contact profile.

        Args:
            contact_id (int): The database ID of the contact

        Returns:
            Optional[ContactProfileResponse]: Detailed contact profile if found
        """
        # Retrieve base contact
        contact = await self.get_by_id(contact_id)

        if not contact:
            return None

        # Construct detailed profile
        return ContactProfileResponse(
            contact=contact,
            tags=[],  # Placeholder, should be populated with actual tags
            mutual_groups=[],  # Placeholder, should be populated with actual groups
            last_received_message=None,  # Placeholder for last received message
            last_sent_message=None,  # Placeholder for last sent message
        )

"""
Async Tag Repository for managing tag entities and contact-tag associations.

Provides asynchronous CRUD operations for tags and management of the
many-to-many relationship between contacts and tags using SQLAlchemy.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.models.tag import Tag, contact_tags
from src.models.contact import Contact


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
        self.session = session

    async def create(self, tag_data: Dict[str, Any]) -> Tag:
        """
        Asynchronously create a new tag.

        Args:
            tag_data (Dict[str, Any]): Data for creating a new tag
                Required: name
                Optional: color, created_at

        Returns:
            Tag: The newly created tag

        Raises:
            ValueError: If tag creation fails or name already exists
        """
        try:
            # Set default timestamp if not provided
            tag_data.setdefault("created_at", datetime.utcnow())

            # Remove id if present to allow SQLAlchemy to generate
            if "id" in tag_data and tag_data["id"] is None:
                del tag_data["id"]

            tag = Tag(**tag_data)
            self.session.add(tag)
            await self.session.commit()
            await self.session.refresh(tag)
            return tag
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(
                f"Tag with name '{tag_data.get('name')}' already exists"
            ) from e
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to create tag: {str(e)}") from e

    async def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """
        Retrieve a tag by its database ID.

        Args:
            tag_id (int): The unique database ID of the tag

        Returns:
            Optional[Tag]: The tag if found, None otherwise
        """
        return await self.session.get(Tag, tag_id)

    async def get_by_name(self, name: str) -> Optional[Tag]:
        """
        Retrieve a tag by its name (case-insensitive).

        Args:
            name (str): The tag name to search for

        Returns:
            Optional[Tag]: The tag if found, None otherwise
        """
        query = select(Tag).where(func.lower(Tag.name) == name.lower())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Tag]:
        """
        Retrieve all tags with optional pagination.

        Args:
            limit (Optional[int]): Maximum number of records to return
            offset (int): Number of records to skip

        Returns:
            List[Tag]: List of tags ordered by name
        """
        query = select(Tag).order_by(Tag.name)

        if limit is not None:
            query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, tag_id: int, update_data: Dict[str, Any]) -> Optional[Tag]:
        """
        Update an existing tag.

        Args:
            tag_id (int): ID of the tag to update
            update_data (Dict[str, Any]): Fields to update (name, color)

        Returns:
            Optional[Tag]: Updated tag, or None if not found

        Raises:
            ValueError: If update fails or new name already exists
        """
        try:
            # Fetch the existing tag
            tag = await self.get_by_id(tag_id)
            if not tag:
                return None

            # Update fields
            for key, value in update_data.items():
                if hasattr(tag, key) and key != "id":
                    setattr(tag, key, value)

            await self.session.commit()
            await self.session.refresh(tag)
            return tag

        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(
                f"Tag name already exists: {update_data.get('name')}"
            ) from e
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to update tag: {str(e)}") from e

    async def delete(self, tag_id: int) -> bool:
        """
        Delete a tag by its database ID.

        This will also remove all contact-tag associations due to CASCADE.

        Args:
            tag_id (int): ID of the tag to delete

        Returns:
            bool: True if tag was deleted, False if not found
        """
        try:
            tag = await self.get_by_id(tag_id)
            if not tag:
                return False

            await self.session.delete(tag)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False

    async def get_tags_for_contact(self, contact_id: int) -> List[Tag]:
        """
        Retrieve all tags associated with a specific contact.

        Args:
            contact_id (int): The database ID of the contact

        Returns:
            List[Tag]: List of tags assigned to the contact, ordered by name
        """
        query = (
            select(Tag)
            .join(contact_tags, Tag.id == contact_tags.c.tag_id)
            .where(contact_tags.c.contact_id == contact_id)
            .order_by(Tag.name)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_tag_to_contact(self, contact_id: int, tag_id: int) -> bool:
        """
        Add a tag to a contact (create association).

        Args:
            contact_id (int): The database ID of the contact
            tag_id (int): The database ID of the tag

        Returns:
            bool: True if association was created, False if it already existed

        Raises:
            ValueError: If contact or tag doesn't exist
        """
        try:
            # Verify contact and tag exist
            contact = await self.session.get(Contact, contact_id)
            tag = await self.get_by_id(tag_id)

            if not contact:
                raise ValueError(f"Contact with ID {contact_id} not found")
            if not tag:
                raise ValueError(f"Tag with ID {tag_id} not found")

            # Check if association already exists
            query = select(contact_tags).where(
                and_(
                    contact_tags.c.contact_id == contact_id,
                    contact_tags.c.tag_id == tag_id,
                )
            )
            result = await self.session.execute(query)
            if result.first() is not None:
                return False  # Association already exists

            # Create association
            stmt = contact_tags.insert().values(
                contact_id=contact_id, tag_id=tag_id, created_at=datetime.utcnow()
            )
            await self.session.execute(stmt)
            await self.session.commit()
            return True

        except ValueError:
            raise
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to add tag to contact: {str(e)}") from e

    async def remove_tag_from_contact(self, contact_id: int, tag_id: int) -> bool:
        """
        Remove a tag from a contact (delete association).

        Args:
            contact_id (int): The database ID of the contact
            tag_id (int): The database ID of the tag

        Returns:
            bool: True if association was removed, False if it didn't exist
        """
        try:
            stmt = delete(contact_tags).where(
                and_(
                    contact_tags.c.contact_id == contact_id,
                    contact_tags.c.tag_id == tag_id,
                )
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0

        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Failed to remove tag from contact: {str(e)}") from e

    async def get_contacts_by_tag(self, tag_id: int) -> List[Contact]:
        """
        Retrieve all contacts associated with a specific tag.

        Args:
            tag_id (int): The database ID of the tag

        Returns:
            List[Contact]: List of contacts with this tag, ordered by display_name
        """
        query = (
            select(Contact)
            .join(contact_tags, Contact.id == contact_tags.c.contact_id)
            .where(contact_tags.c.tag_id == tag_id)
            .order_by(Contact.display_name)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_contacts_by_tags(self, tag_ids: List[int]) -> List[Contact]:
        """
        Retrieve all contacts that have ANY of the specified tags.

        Args:
            tag_ids (List[int]): List of tag IDs to filter by

        Returns:
            List[Contact]: List of unique contacts with any of the specified tags
        """
        if not tag_ids:
            return []

        query = (
            select(Contact)
            .join(contact_tags, Contact.id == contact_tags.c.contact_id)
            .where(contact_tags.c.tag_id.in_(tag_ids))
            .distinct()
            .order_by(Contact.display_name)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_tag_count_for_contact(self, contact_id: int) -> int:
        """
        Get the number of tags assigned to a contact.

        Args:
            contact_id (int): The database ID of the contact

        Returns:
            int: Number of tags assigned to the contact
        """
        query = (
            select(func.count())
            .select_from(contact_tags)
            .where(contact_tags.c.contact_id == contact_id)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_contact_count_for_tag(self, tag_id: int) -> int:
        """
        Get the number of contacts assigned to a tag.

        Args:
            tag_id (int): The database ID of the tag

        Returns:
            int: Number of contacts with this tag
        """
        query = (
            select(func.count())
            .select_from(contact_tags)
            .where(contact_tags.c.tag_id == tag_id)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def exists_by_name(self, name: str) -> bool:
        """
        Check if a tag exists with the given name (case-insensitive).

        Args:
            name (str): Tag name to check

        Returns:
            bool: True if tag exists, False otherwise
        """
        tag = await self.get_by_name(name)
        return tag is not None

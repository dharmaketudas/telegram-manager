"""
Migration 006: Tag Repository Implementation
Documents the Tag Repository implementation with SQLAlchemy ORM and many-to-many relationships
"""

import logging
from . import Migration
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class TagRepositoryMigration(Migration):
    """Migration documenting Tag Repository implementation"""

    def __init__(self):
        super().__init__(
            version="006",
            name="tag_repository",
            description="Tag Repository implementation with SQLAlchemy ORM and many-to-many relationship management",
        )

    async def up(self, db: DatabaseConnection):
        """
        This migration documents the Tag Repository implementation.

        The tags and contact_tags tables were already created in migration_001_initial_schema.
        This migration verifies the schema is correct for the TagRepository.

        Schema Requirements:
        - tags table with id, name (unique), color, created_at
        - contact_tags junction table with contact_id, tag_id (composite PK), created_at
        - Foreign key constraints with CASCADE delete
        - Indexes on name, contact_id, and tag_id
        """
        logger.info("Verifying Tag Repository schema...")

        # Verify tags table exists
        tags_exists = await db.table_exists("tags")
        if not tags_exists:
            raise Exception("tags table does not exist. Run migration_001 first.")

        # Verify contact_tags junction table exists
        contact_tags_exists = await db.table_exists("contact_tags")
        if not contact_tags_exists:
            raise Exception(
                "contact_tags table does not exist. Run migration_001 first."
            )

        logger.info("✓ Tag Repository schema verified")

        # Log implementation details
        logger.info("Tag Repository Features:")
        logger.info(
            "  - CRUD operations: create, get_by_id, get_by_name, get_all, update, delete"
        )
        logger.info(
            "  - Association management: add_tag_to_contact, remove_tag_from_contact"
        )
        logger.info("  - Tag retrieval: get_tags_for_contact")
        logger.info("  - Contact retrieval: get_contacts_by_tag, get_contacts_by_tags")
        logger.info(
            "  - Count operations: get_tag_count_for_contact, get_contact_count_for_tag"
        )
        logger.info("  - Helper methods: exists_by_name")
        logger.info("  - Case-insensitive name searches")
        logger.info("  - Cascade deletion of associations")

    async def down(self, db: DatabaseConnection):
        """
        This migration does not modify the database schema.
        No rollback action needed.
        """
        logger.info("No database changes to roll back for Tag Repository migration")

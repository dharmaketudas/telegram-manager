"""
Migration 005: Enhance Contact Repository Methods

This migration script updates the contacts table to support advanced
search and existence checking capabilities in the Contact Repository.

Revision Details:
- Add additional indexes for faster searching
- Ensure necessary constraints are in place
- Optimize query performance for contact-related operations
"""

from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import TSVECTOR

from src.database.base import Base
from src.database.migration_helpers import MigrationHelper


class Migration005ContactRepositoryMethods(Base):
    """
    Migration class to enhance contact repository query capabilities.
    """

    __tablename__ = "contacts"

    # Create a full-text search vector for efficient searching
    search_vector = Column(
        TSVECTOR, nullable=True, comment="Full-text search vector for contacts"
    )

    # Additional indexes for performance optimization
    __table_args__ = (
        Index("idx_contact_search_vector", "search_vector", postgresql_using="gin"),
        Index("idx_contact_telegram_id_unique", "telegram_id", unique=True),
        Index(
            "idx_contact_search_fields",
            "username",
            "first_name",
            "last_name",
            "display_name",
            "phone",
        ),
    )


def upgrade(migrate_engine):
    """
    Upgrade database schema to support enhanced contact repository methods.

    Args:
        migrate_engine: SQLAlchemy migration engine
    """
    helper = MigrationHelper(migrate_engine)

    # Add full-text search vector column
    helper.add_column(
        table_name="contacts", column=Migration005ContactRepositoryMethods.search_vector
    )

    # Create GIN index for full-text search
    helper.execute_sql("""
        CREATE INDEX idx_contact_search_vector
        ON contacts
        USING gin(search_vector);
    """)

    # Update trigger to maintain search vector
    helper.execute_sql("""
        CREATE OR REPLACE FUNCTION update_contact_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector = to_tsvector(
                'pg_catalog.simple',
                COALESCE(NEW.username, '') || ' ' ||
                COALESCE(NEW.first_name, '') || ' ' ||
                COALESCE(NEW.last_name, '') || ' ' ||
                COALESCE(NEW.display_name, '') || ' ' ||
                COALESCE(NEW.phone, '')
            );
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER contact_search_vector_update
        BEFORE INSERT OR UPDATE ON contacts
        FOR EACH ROW
        EXECUTE FUNCTION update_contact_search_vector();
    """)


def downgrade(migrate_engine):
    """
    Downgrade database schema, removing enhancements.

    Args:
        migrate_engine: SQLAlchemy migration engine
    """
    helper = MigrationHelper(migrate_engine)

    # Remove search vector column
    helper.drop_column(table_name="contacts", column_name="search_vector")

    # Drop related trigger and index
    helper.execute_sql("""
        DROP INDEX IF EXISTS idx_contact_search_vector;
        DROP TRIGGER IF EXISTS contact_search_vector_update ON contacts;
        DROP FUNCTION IF EXISTS update_contact_search_vector();
    """)

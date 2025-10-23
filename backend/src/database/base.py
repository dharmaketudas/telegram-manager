"""
Database Base Configuration

This module defines the base declarative class for SQLAlchemy models,
providing a foundation for creating database models with common configurations
and utility methods.
"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr

from typing import Any


class Base(DeclarativeBase):
    """
    Base declarative class for all database models.

    Provides common configuration and utility methods for SQLAlchemy models.
    """

    # Automatically generate lowercase, pluralized table names
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Generate table names automatically from class names.

        Converts CamelCase class names to snake_case table names.
        Example: UserProfile -> user_profiles

        Returns:
            str: Pluralized, lowercase table name
        """
        return f"{cls.__name__.lower()}s"

    # Optional common columns that can be inherited by all models
    id: Mapped[int] = mapped_column(primary_key=True)

    # Optional timestamp columns
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """
        Provide a helpful string representation of the model.

        Returns a string showing the model's class name and primary key value.

        Returns:
            str: String representation of the model instance
        """
        pk = getattr(self, "id", None)
        return f"<{self.__class__.__name__} id={pk}>"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to a dictionary.

        Useful for serialization and API responses.

        Returns:
            dict: Dictionary representation of the model instance
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

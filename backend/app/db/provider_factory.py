from typing import Type, TypeVar, Any

from app.db.base import DatabaseProvider
from app.db.sql import SQLProvider
from app.db.session import get_session_factory

T = TypeVar("T")
ID = TypeVar("ID")


class ProviderFactory:
    """Factory for creating database providers."""

    @staticmethod
    def get_provider(
        pydantic_model: Type[T],
        orm_model: Type[Any],
    ) -> DatabaseProvider[T, ID]:
        """Get the appropriate SQL database provider."""

        # Get the correct session factory based on configured database type
        session_factory = get_session_factory()

        # Create and return the SQL provider
        return SQLProvider(
            pydantic_model=pydantic_model,
            orm_model=orm_model,
            session_factory=session_factory,
        )

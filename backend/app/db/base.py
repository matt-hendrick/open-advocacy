from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

T = TypeVar("T")
ID = TypeVar("ID")


class DatabaseProvider(ABC, Generic[T, ID]):
    """Abstract base class for database providers."""

    @abstractmethod
    async def get(self, id: ID) -> T | None:
        """Get an item by ID."""
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        """List all items with pagination."""
        pass

    @abstractmethod
    async def create(self, obj_in: Any) -> T:
        """Create a new item."""
        pass

    @abstractmethod
    async def update(self, id: ID, obj_in: Any) -> T | None:
        """Update an existing item."""
        pass

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """Delete an item by ID."""
        pass

    @abstractmethod
    async def filter(self, **filters) -> list[T]:
        """
        Filter items by field equality.

        Args:
            **filters: Field-value pairs for equality filtering (field=value)

        Returns:
            List of items matching the filter criteria
        """
        pass

    @abstractmethod
    async def filter_in(self, field: str, values: list[Any]) -> list[T]:
        """
        Filter items where a field value is in a list of values.

        Args:
            field: The field to check
            values: List of values to match against

        Returns:
            List of items where the field value is in the provided list
        """
        pass

    @abstractmethod
    async def filter_multiple(
        self, filters: dict[str, Any], in_filters: dict[str, list[Any]] | None = None
    ) -> List[T]:
        """
        Filter items by multiple conditions including both equality and IN clauses.

        Args:
            filters: Dict of field=value for equality filters
            in_filters: Dict of field=[values] for IN filters

        Returns:
            List of items matching all the filter criteria
        """
        pass

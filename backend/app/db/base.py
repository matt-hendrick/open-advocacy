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

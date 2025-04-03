from abc import ABC, abstractmethod
from typing import Any
from app.models.pydantic.models import Entity


class LocationModule(ABC):
    """Base interface for location modules that handle address to representative lookups."""

    @abstractmethod
    async def find_representatives_by_address(self, address: str) -> list[Entity]:
        """
        Translates an address to a list of representatives.

        Args:
            address: A string address to lookup

        Returns:
            A list of Entity objects representing the officials for this address
        """
        pass

    @abstractmethod
    async def get_jurisdiction_boundaries(self) -> dict[str, Any]:
        """
        Returns jurisdiction boundaries in GeoJSON format.

        Returns:
            A dictionary containing GeoJSON data
        """
        pass

    @abstractmethod
    def get_entity_types(self) -> list[str]:
        """
        Returns the entity types available for this location.

        Returns:
            A list of entity type strings (e.g., ["alderman", "state_rep", "governor"])
        """
        pass

    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """
        Validates if an address is properly formatted for this location.

        Args:
            address: A string address to validate

        Returns:
            True if the address is valid, False otherwise
        """
        pass

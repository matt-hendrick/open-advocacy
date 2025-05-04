from abc import ABC, abstractmethod
from typing import Any


class LocationConfig(ABC):
    """Base class for location configurations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the location."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the location."""
        pass

    @property
    @abstractmethod
    def import_steps(self) -> list[dict[str, Any]]:
        """Ordered steps for importing this location's data."""
        pass

    @abstractmethod
    async def get_importers(self) -> dict[str, Any]:
        """Get configured importers for this location."""
        pass

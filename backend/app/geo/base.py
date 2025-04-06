from abc import ABC, abstractmethod
from typing import List, Dict, Any
from uuid import UUID


class GeoProvider(ABC):
    """Interface for geographic operations"""

    @abstractmethod
    async def point_in_jurisdictions(self, lat: float, lon: float) -> List[UUID]:
        """
        Find all jurisdiction IDs that contain the given point

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            List of jurisdiction IDs
        """
        pass

    @abstractmethod
    async def store_jurisdiction_boundary(
        self, jurisdiction_id: UUID, geojson: Dict[str, Any]
    ) -> bool:
        """
        Store a boundary for a jurisdiction

        Args:
            jurisdiction_id: ID of the jurisdiction
            geojson: GeoJSON boundary data

        Returns:
            Success flag
        """
        pass

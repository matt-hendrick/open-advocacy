from abc import ABC, abstractmethod
from typing import List, Any
from uuid import UUID


class GeoProvider(ABC):
    """Base interface for geographic operations"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    @abstractmethod
    async def districts_containing_point(self, lat: float, lon: float) -> List[UUID]:
        """Find all district IDs that contain the given point"""
        pass

    @abstractmethod
    async def store_district_boundary(
        self, district_id: UUID, geojson: dict[str, Any]
    ) -> bool:
        """Store a boundary for a district"""
        pass

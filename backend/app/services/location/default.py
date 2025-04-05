from typing import Any
import uuid

from app.services.location.base import LocationModule
from app.models.pydantic.models import Entity


class DefaultLocationModule(LocationModule):
    """Default implementation of the location module with mock data."""

    async def find_representatives_by_address(self, address: str) -> list[Entity]:
        """Returns mock representatives for any address."""
        # In a real implementation, this would query an external service
        return [
            Entity(
                name="Jane Doe",
                title="Representative",
                entity_type="default_rep",
                jurisdiction_id=uuid.uuid4(),
                email="jane.doe@example.gov",
                phone="555-123-4567",
                website="https://example.gov/janedoe",
                address="123 Government St, City, State 12345",
            ),
            Entity(
                name="John Smith",
                title="Senator",
                entity_type="default_sen",
                jurisdiction_id=uuid.uuid4(),
                email="john.smith@example.gov",
                phone="555-765-4321",
                website="https://example.gov/johnsmith",
                address="456 Capitol Ave, City, State 12345",
            ),
            Entity(
                name="Bob James",
                title="Alderman",
                entity_type="default_alder",
                jurisdiction_id=uuid.uuid4(),
                email="bob.james@example.gov",
                phone="555-12e-4567",
                website="https://example.gov/bobjames",
                address="124 Government St, City, State 12345",
            ),
        ]

    async def get_jurisdiction_boundaries(self) -> dict[str, Any]:
        """Returns a simple mock boundary."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Default Jurisdiction"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-100.0, 40.0],
                                [-100.0, 45.0],
                                [-90.0, 45.0],
                                [-90.0, 40.0],
                                [-100.0, 40.0],
                            ]
                        ],
                    },
                }
            ],
        }

    def get_entity_types(self) -> list[str]:
        """Returns the available entity types for this module."""
        return ["default_rep", "default_sen", "default_alder"]

    def validate_address(self, address: str) -> bool:
        """Validates the address format - accepts anything in the default implementation."""
        return True if address else False

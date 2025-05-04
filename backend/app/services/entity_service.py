from uuid import UUID

from app.models.pydantic.models import Entity, EntityCreate, AddressLookupRequest
from app.db.base import DatabaseProvider
from app.geo.geocoding_service import GeocodingService


class EntityService:
    def __init__(
        self,
        entities_provider: DatabaseProvider,
        jurisdictions_provider: DatabaseProvider,
        districts_provider: DatabaseProvider,
        geo_provider=None,
    ):
        self.entities_provider = entities_provider
        self.jurisdictions_provider = jurisdictions_provider
        self.districts_provider = districts_provider
        self.geo_provider = geo_provider
        self.geocoding_service = GeocodingService()

    async def list_entities(self, jurisdiction_id: UUID) -> list[Entity]:
        """List entities by jurisdiction with district name enrichment."""
        entities = await self.entities_provider.filter(jurisdiction_id=jurisdiction_id)
        for entity in entities:
            district = await self.districts_provider.get(entity.district_id)
            if district:
                entity.district_name = district.name
        return entities

    async def create_entity(self, entity: EntityCreate) -> Entity:
        """Create a new entity after validating the jurisdiction."""
        # Verify jurisdiction exists
        jurisdiction = await self.jurisdictions_provider.get(entity.jurisdiction_id)
        if not jurisdiction:
            raise ValueError("Jurisdiction not found")

        return await self.entities_provider.create(entity)

    async def get_entity(self, entity_id: UUID) -> Entity | None:
        """Get an entity by ID."""
        return await self.entities_provider.get(entity_id)

    async def update_entity(
        self, entity_id: UUID, entity: EntityCreate
    ) -> Entity | None:
        """Update an existing entity."""
        existing_entity = await self.entities_provider.get(entity_id)
        if not existing_entity:
            return None

        return await self.entities_provider.update(entity_id, entity)

    async def delete_entity(self, entity_id: UUID) -> bool:
        """Delete an entity by ID."""
        existing_entity = await self.entities_provider.get(entity_id)
        if not existing_entity:
            return False

        return await self.entities_provider.delete(entity_id)

    async def lookup_entities_by_address(
        self, request: AddressLookupRequest
    ) -> list[Entity]:
        """Look up entities for a given address."""
        if not self.geo_provider:
            raise ValueError("Geo provider is required for address lookup")

        # 1. Geocode the address to get coordinates
        lat, lon = await self.geocoding_service.geocode_address(address=request.address)

        # 2. Find districts containing this point
        district_ids = await self.geo_provider.districts_containing_point(lat, lon)

        # 3. Find entities for these districts
        entities = await self.entities_provider.filter_multiple(
            filters={}, in_filters={"district_id": district_ids}
        )

        # 4. Enhance with district and jurisdiction names
        for entity in entities:
            district = await self.districts_provider.get(entity.district_id)
            if district:
                entity.district_name = district.name

        return entities

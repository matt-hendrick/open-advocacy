from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.models.pydantic.models import Entity, EntityCreate, AddressLookupRequest
from app.db.base import DatabaseProvider
from app.db.dependencies import (
    get_entities_provider,
    get_jurisdictions_provider,
    get_districts_provider,
)
from typing import List
from app.geo.geocoding_service import GeocodingService
from app.geo.provider_factory import get_geo_provider

router = APIRouter()
geocoding_service = GeocodingService()


@router.get("/", response_model=list[Entity])
async def list_entities(
    jurisdiction_id: UUID,
    entities_provider: DatabaseProvider = Depends(get_entities_provider),
    districts_provider=Depends(get_districts_provider),
):
    entities = await entities_provider.filter(jurisdiction_id=jurisdiction_id)
    for entity in entities:
        district = await districts_provider.get(entity.district_id)
        if district:
            entity.district_name = district.name
    return entities


@router.post("/", response_model=Entity)
async def create_entity(
    entity: EntityCreate,
    entities_provider: DatabaseProvider = Depends(get_entities_provider),
    jurisdictions_provider: DatabaseProvider = Depends(get_jurisdictions_provider),
):
    # Verify jurisdiction exists
    jurisdiction = await jurisdictions_provider.get(entity.jurisdiction_id)
    if not jurisdiction:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")

    return await entities_provider.create(entity)


@router.get("/{entity_id}", response_model=Entity)
async def get_entity(
    entity_id: UUID,
    entities_provider: DatabaseProvider = Depends(get_entities_provider),
):
    entity = await entities_provider.get(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.put("/{entity_id}", response_model=Entity)
async def update_entity(
    entity_id: UUID,
    entity: EntityCreate,
    entities_provider: DatabaseProvider = Depends(get_entities_provider),
):
    existing_entity = await entities_provider.get(entity_id)
    if not existing_entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return await entities_provider.update(entity_id, entity)


@router.delete("/{entity_id}", response_model=bool)
async def delete_entity(
    entity_id: UUID,
    entities_provider: DatabaseProvider = Depends(get_entities_provider),
):
    existing_entity = await entities_provider.get(entity_id)
    if not existing_entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return await entities_provider.delete(entity_id)


@router.post("/address_lookup", response_model=List[Entity])
async def lookup_entities_by_address(
    request: AddressLookupRequest,
    geo_provider=Depends(get_geo_provider),
    entities_provider=Depends(get_entities_provider),
    districts_provider=Depends(get_districts_provider),
):
    """Look up entities for a given address"""

    # 1. Geocode the address to get coordinates
    lat, lon = await geocoding_service.geocode_address(address=request.address)

    # 2. Find districts containing this point
    district_ids = await geo_provider.districts_containing_point(lat, lon)

    # 3. Find entities for these districts
    entities = await entities_provider.filter_multiple(
        filters={}, in_filters={"district_id": district_ids}
    )

    # 4. Enhance with district and jurisdiction names
    for entity in entities:
        district = await districts_provider.get(entity.district_id)
        if district:
            entity.district_name = district.name

    return entities

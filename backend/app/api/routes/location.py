from fastapi import APIRouter, Depends
from typing import List
from app.geo.geocoding_service import GeocodingService
from app.models.pydantic.models import Entity, AddressLookupRequest
from app.geo.provider_factory import get_geo_provider
from app.db.dependencies import get_entities_provider, get_districts_provider

router = APIRouter()
geocoding_service = GeocodingService()


@router.post("/lookup", response_model=List[Entity])
async def lookup_representatives(
    request: AddressLookupRequest,
    geo_provider=Depends(get_geo_provider),
    entities_provider=Depends(get_entities_provider),
    districts_provider=Depends(get_districts_provider),
):
    """Look up representatives for a given address"""

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

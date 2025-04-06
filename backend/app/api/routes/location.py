from fastapi import APIRouter, Depends
from app.models.pydantic.models import Entity, AddressLookupRequest
from app.geo.geocoding_service import GeocodingService
from app.geo.provider_factory import get_geo_provider
from app.geo.base import GeoProvider
from app.db.dependencies import get_entities_provider, get_jurisdictions_provider
from app.db.base import DatabaseProvider
from uuid import UUID
from pydantic import BaseModel

router = APIRouter()
geocoding_service = GeocodingService()


class JurisdictionWithEntities(BaseModel):
    id: UUID
    name: str
    level: str
    description: str | None = None
    entities: list[Entity] = []


class AddressLookupResponse(BaseModel):
    address: str
    coordinates: tuple[float, float]  # [latitude, longitude]
    jurisdictions: list[JurisdictionWithEntities] = []


# @router.post("/lookup", response_model=list[Entity])
# async def lookup_representatives(
#     request: AddressLookupRequest,
#     geo_provider: GeoProvider = Depends(get_geo_provider),
#     entities_provider: DatabaseProvider = Depends(get_entities_provider),
# ):
#     """Look up representatives for a given address."""

#     # 1. Geocode the address
#     try:
#         lat, lon = await geocoding_service.geocode_address(request.address)
#     except HTTPException as e:
#         raise e

#     # 2. Find jurisdictions containing this point
#     jurisdiction_ids = await geo_provider.point_in_jurisdictions(lat, lon)

#     # 3. If no jurisdictions found, return empty list
#     if not jurisdiction_ids:
#         return []

#     # 4. Find entities for these jurisdictions
#     entities = await entities_provider.filter_multiple(
#         filters={}, in_filters={"jurisdiction_id": jurisdiction_ids}
#     )

#     return entities


@router.post("/lookup", response_model=AddressLookupResponse)
async def lookup_representatives(
    request: AddressLookupRequest,
    geo_provider: GeoProvider = Depends(get_geo_provider),
    jurisdictions_provider: DatabaseProvider = Depends(get_jurisdictions_provider),
    entities_provider: DatabaseProvider = Depends(get_entities_provider),
):
    """Look up representatives for a given address."""

    # 1. Geocode the address
    lat, lon = await geocoding_service.geocode_address(request.address)

    # 2. Find jurisdictions containing this point
    jurisdiction_ids = await geo_provider.point_in_jurisdictions(lat, lon)

    # 3. If no jurisdictions found, return empty response
    if not jurisdiction_ids:
        return AddressLookupResponse(
            address=request.address, coordinates=(lat, lon), jurisdictions=[]
        )

    # 4. Get jurisdiction details
    jurisdictions = []
    print("jurisdiction_ids", jurisdiction_ids)
    for jid in jurisdiction_ids:
        jurisdiction = await jurisdictions_provider.get(jid)
        print("jurisdiction", jurisdiction)
        if jurisdiction:
            # 5. Find entities for this jurisdiction
            entities = await entities_provider.filter(jurisdiction_id=jid)
            print("entities", entities)

            # 6. Create response object
            jurisdictions.append(
                JurisdictionWithEntities(
                    id=jurisdiction.id,
                    name=jurisdiction.name,
                    level=jurisdiction.level,
                    description=jurisdiction.description,
                    entities=entities,
                )
            )

    # 7. Return complete response
    return AddressLookupResponse(
        address=request.address, coordinates=(lat, lon), jurisdictions=jurisdictions
    )

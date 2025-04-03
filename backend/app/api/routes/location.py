from fastapi import APIRouter, HTTPException

from app.models.pydantic.models import Entity, AddressLookupRequest
from app.services.location.factory import get_location_module, list_available_modules

router = APIRouter()


@router.post("/lookup", response_model=list[Entity])
async def lookup_representatives(
    request: AddressLookupRequest, module_id: str = "default"
):
    """Look up representatives for a given address using a specific location module."""
    location_module = get_location_module(module_id)

    if not location_module.validate_address(request.address):
        raise HTTPException(status_code=400, detail="Invalid address format")

    return await location_module.find_representatives_by_address(request.address)


@router.get("/modules", response_model=dict[str, str])
async def get_available_modules():
    """Get a list of available location modules."""
    return list_available_modules()


@router.get("/entity-types", response_model=list[str])
async def get_entity_types(module_id: str = "default"):
    """Get a list of entity types for a specific location module."""
    location_module = get_location_module(module_id)
    return location_module.get_entity_types()

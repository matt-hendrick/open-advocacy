from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.models.pydantic.models import Jurisdiction, JurisdictionBase
from app.services.jurisdiction_service import JurisdictionService
from app.services.service_factory import get_jurisdiction_service

router = APIRouter()


@router.get("/", response_model=list[Jurisdiction])
async def list_jurisdictions(
    skip: int = 0,
    limit: int = 100,
    jurisdiction_service: JurisdictionService = Depends(get_jurisdiction_service),
):
    """List all jurisdictions."""
    return await jurisdiction_service.list_jurisdictions(skip=skip, limit=limit)


@router.post("/", response_model=Jurisdiction)
async def create_jurisdiction(
    jurisdiction: JurisdictionBase,
    jurisdiction_service: JurisdictionService = Depends(get_jurisdiction_service),
):
    """Create a new jurisdiction."""
    return await jurisdiction_service.create_jurisdiction(jurisdiction)


@router.get("/{jurisdiction_id}", response_model=Jurisdiction)
async def get_jurisdiction(
    jurisdiction_id: UUID,
    jurisdiction_service: JurisdictionService = Depends(get_jurisdiction_service),
):
    """Get a jurisdiction by ID."""
    jurisdiction = await jurisdiction_service.get_jurisdiction(jurisdiction_id)
    if not jurisdiction:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    return jurisdiction


@router.put("/{jurisdiction_id}", response_model=Jurisdiction)
async def update_jurisdiction(
    jurisdiction_id: UUID,
    jurisdiction: JurisdictionBase,
    jurisdiction_service: JurisdictionService = Depends(get_jurisdiction_service),
):
    """Update an existing jurisdiction."""
    existing_jurisdiction = await jurisdiction_service.get_jurisdiction(jurisdiction_id)
    if not existing_jurisdiction:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")

    return await jurisdiction_service.update_jurisdiction(jurisdiction_id, jurisdiction)


@router.delete("/{jurisdiction_id}", response_model=bool)
async def delete_jurisdiction(
    jurisdiction_id: UUID,
    jurisdiction_service: JurisdictionService = Depends(get_jurisdiction_service),
):
    """Delete a jurisdiction by ID."""
    existing_jurisdiction = await jurisdiction_service.get_jurisdiction(jurisdiction_id)
    if not existing_jurisdiction:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")

    return await jurisdiction_service.delete_jurisdiction(jurisdiction_id)

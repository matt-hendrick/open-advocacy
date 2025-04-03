from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.models.pydantic.models import Jurisdiction, JurisdictionCreate
from app.db.base import InMemoryProvider
from app.db.dependencies import get_jurisdictions_provider

router = APIRouter()


@router.get("/", response_model=list[Jurisdiction])
async def list_jurisdictions(
    jurisdictions_provider: InMemoryProvider = Depends(get_jurisdictions_provider),
):
    return await jurisdictions_provider.list()


@router.post("/", response_model=Jurisdiction)
async def create_jurisdiction(
    jurisdiction: JurisdictionCreate,
    jurisdictions_provider: InMemoryProvider = Depends(get_jurisdictions_provider),
):
    return await jurisdictions_provider.create(jurisdiction)


@router.get("/{jurisdiction_id}", response_model=Jurisdiction)
async def get_jurisdiction(
    jurisdiction_id: UUID,
    jurisdictions_provider: InMemoryProvider = Depends(get_jurisdictions_provider),
):
    jurisdiction = await jurisdictions_provider.get(jurisdiction_id)
    if not jurisdiction:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    return jurisdiction


@router.put("/{jurisdiction_id}", response_model=Jurisdiction)
async def update_jurisdiction(
    jurisdiction_id: UUID,
    jurisdiction: JurisdictionCreate,
    jurisdictions_provider: InMemoryProvider = Depends(get_jurisdictions_provider),
):
    existing_jurisdiction = await jurisdictions_provider.get(jurisdiction_id)
    if not existing_jurisdiction:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")

    return await jurisdictions_provider.update(jurisdiction_id, jurisdiction)


@router.delete("/{jurisdiction_id}", response_model=bool)
async def delete_jurisdiction(
    jurisdiction_id: UUID,
    jurisdictions_provider: InMemoryProvider = Depends(get_jurisdictions_provider),
):
    existing_jurisdiction = await jurisdictions_provider.get(jurisdiction_id)
    if not existing_jurisdiction:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")

    return await jurisdictions_provider.delete(jurisdiction_id)

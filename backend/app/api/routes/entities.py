from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.models.pydantic.models import Entity, EntityCreate
from app.db.base import DatabaseProvider
from app.db.dependencies import get_entities_provider, get_jurisdictions_provider

router = APIRouter()


@router.get("/", response_model=list[Entity])
async def list_entities(
    jurisdiction_id: str | None = None,
    entity_type: str | None = None,
    entities_provider: DatabaseProvider = Depends(get_entities_provider),
):
    entities = await entities_provider.list()

    # Filter by jurisdiction_id if provided
    if jurisdiction_id:
        entities = [e for e in entities if e.jurisdiction_id == jurisdiction_id]

    # Filter by entity_type if provided
    if entity_type:
        entities = [e for e in entities if e.entity_type == entity_type]

    return entities


@router.get("/by-jurisdictions", response_model=list[Entity])
async def get_entities_by_jurisdiction(
    jurisdiction_id: UUID,
    entities_provider: DatabaseProvider = Depends(get_entities_provider),
):
    entities = await entities_provider.list()
    filtered_entities = [
        entity for entity in entities if entity.jurisdiction_id == jurisdiction_id
    ]
    return filtered_entities


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

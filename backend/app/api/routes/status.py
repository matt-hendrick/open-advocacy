from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.models.pydantic.models import EntityStatusRecord
from app.db.base import InMemoryProvider
from app.db.dependencies import (
    get_status_records_provider,
    get_projects_provider,
    get_entities_provider,
)

router = APIRouter()


@router.get("/", response_model=list[EntityStatusRecord] | None)
async def list_status_records(
    project_id: UUID | None = None,
    entity_id: UUID | None = None,
    status_records_provider: InMemoryProvider = Depends(get_status_records_provider),
):
    status_records = await status_records_provider.list()

    # Filter by project_id if provided
    if project_id:
        status_records = [sr for sr in status_records if sr.project_id == project_id]

    # Filter by entity_id if provided
    if entity_id:
        status_records = [sr for sr in status_records if sr.entity_id == entity_id]

    return status_records


@router.post("/", response_model=EntityStatusRecord)
async def create_status_record(
    status_record: EntityStatusRecord,
    status_records_provider: InMemoryProvider = Depends(get_status_records_provider),
    projects_provider: InMemoryProvider = Depends(get_projects_provider),
    entities_provider: InMemoryProvider = Depends(get_entities_provider),
):
    # Verify project exists
    project = await projects_provider.get(status_record.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify entity exists
    entity = await entities_provider.get(status_record.entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Check if status record already exists for this entity and project
    existing_records = await status_records_provider.list()
    for record in existing_records:
        if (
            record.entity_id == status_record.entity_id
            and record.project_id == status_record.project_id
        ):
            # Update existing record
            updated_record = await status_records_provider.update(
                record.id, status_record
            )
            return updated_record

    return await status_records_provider.create(status_record)


@router.get("/{record_id}", response_model=EntityStatusRecord)
async def get_status_record(
    record_id: UUID,
    status_records_provider: InMemoryProvider = Depends(get_status_records_provider),
):
    record = await status_records_provider.get(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Status record not found")
    return record


@router.put("/{record_id}", response_model=EntityStatusRecord)
async def update_status_record(
    record_id: UUID,
    status_record: EntityStatusRecord,
    status_records_provider: InMemoryProvider = Depends(get_status_records_provider),
):
    existing_record = await status_records_provider.get(record_id)
    if not existing_record:
        raise HTTPException(status_code=404, detail="Status record not found")

    return await status_records_provider.update(record_id, status_record)


@router.delete("/{record_id}", response_model=bool)
async def delete_status_record(
    record_id: UUID,
    status_records_provider: InMemoryProvider = Depends(get_status_records_provider),
):
    existing_record = await status_records_provider.get(record_id)
    if not existing_record:
        raise HTTPException(status_code=404, detail="Status record not found")

    return await status_records_provider.delete(record_id)

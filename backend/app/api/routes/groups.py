from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.models.pydantic.models import Group, GroupBase
from app.services.group_service import GroupService
from app.services.service_factory import get_group_service

router = APIRouter()


@router.get("/", response_model=list[Group])
async def list_groups(
    group_service: GroupService = Depends(get_group_service),
):
    """List all groups."""
    return await group_service.list_groups()


@router.post("/", response_model=Group)
async def create_group(
    group: GroupBase,
    group_service: GroupService = Depends(get_group_service),
):
    """Create a new group."""
    return await group_service.create_group(group)


@router.get("/{group_id}", response_model=Group)
async def get_group(
    group_id: UUID, group_service: GroupService = Depends(get_group_service)
):
    """Get a group by ID."""
    group = await group_service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.put("/{group_id}", response_model=Group)
async def update_group(
    group_id: UUID,
    group: GroupBase,
    group_service: GroupService = Depends(get_group_service),
):
    """Update an existing group."""
    updated_group = await group_service.update_group(group_id, group)
    if not updated_group:
        raise HTTPException(status_code=404, detail="Group not found")
    return updated_group


@router.delete("/{group_id}", response_model=bool)
async def delete_group(
    group_id: UUID, group_service: GroupService = Depends(get_group_service)
):
    """Delete a group by ID."""
    deleted = await group_service.delete_group(group_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Group not found")
    return deleted

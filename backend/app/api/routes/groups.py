from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.models.pydantic.models import Group, GroupBase
from app.db.base import DatabaseProvider
from app.db.dependencies import get_groups_provider

router = APIRouter()


@router.get("/", response_model=list[Group])
async def list_groups(
    groups_provider: DatabaseProvider = Depends(get_groups_provider),
):
    groups = await groups_provider.list()

    return groups


@router.post("/", response_model=Group)
async def create_group(
    group: GroupBase,
    groups_provider: DatabaseProvider = Depends(get_groups_provider),
):
    return await groups_provider.create(group)


@router.get("/{group_id}", response_model=Group)
async def get_group(
    group_id: UUID, groups_provider: DatabaseProvider = Depends(get_groups_provider)
):
    group = await groups_provider.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.put("/{group_id}", response_model=Group)
async def update_group(
    group_id: UUID,
    group: GroupBase,
    groups_provider: DatabaseProvider = Depends(get_groups_provider),
):
    existing_group = await groups_provider.get(group_id)
    if not existing_group:
        raise HTTPException(status_code=404, detail="Group not found")

    return await groups_provider.update(group_id, group)


@router.delete("/{group_id}", response_model=bool)
async def delete_group(
    group_id: UUID, groups_provider: DatabaseProvider = Depends(get_groups_provider)
):
    existing_group = await groups_provider.get(group_id)
    if not existing_group:
        raise HTTPException(status_code=404, detail="Group not found")

    return await groups_provider.delete(group_id)

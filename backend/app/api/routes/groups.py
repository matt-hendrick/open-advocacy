from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.models.pydantic.models import Group, GroupCreate, GroupStance
from app.db.base import InMemoryProvider
from app.db.dependencies import get_groups_provider, get_projects_provider

router = APIRouter()


@router.get("/", response_model=list[Group])
async def list_groups(
    project_id: UUID | None = None,
    stance: GroupStance | None = None,
    groups_provider: InMemoryProvider = Depends(get_groups_provider),
):
    groups = await groups_provider.list()

    # Filter by project_id if provided
    if project_id:
        groups = [g for g in groups if g.project_id == project_id]

    # Filter by stance if provided
    if stance:
        groups = [g for g in groups if g.stance == stance]

    return groups


@router.post("/", response_model=Group)
async def create_group(
    group: GroupCreate,
    groups_provider: InMemoryProvider = Depends(get_groups_provider),
    projects_provider: InMemoryProvider = Depends(get_projects_provider),
):
    # Verify project exists
    project = await projects_provider.get(group.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await groups_provider.create(group)


@router.get("/{group_id}", response_model=Group)
async def get_group(
    group_id: UUID, groups_provider: InMemoryProvider = Depends(get_groups_provider)
):
    group = await groups_provider.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.put("/{group_id}", response_model=Group)
async def update_group(
    group_id: UUID,
    group: GroupCreate,
    groups_provider: InMemoryProvider = Depends(get_groups_provider),
):
    existing_group = await groups_provider.get(group_id)
    if not existing_group:
        raise HTTPException(status_code=404, detail="Group not found")

    return await groups_provider.update(group_id, group)


@router.delete("/{group_id}", response_model=bool)
async def delete_group(
    group_id: UUID, groups_provider: InMemoryProvider = Depends(get_groups_provider)
):
    existing_group = await groups_provider.get(group_id)
    if not existing_group:
        raise HTTPException(status_code=404, detail="Group not found")

    return await groups_provider.delete(group_id)

from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.models.pydantic.models import Project, ProjectCreate, ProjectStatus
from app.db.base import InMemoryProvider
from app.db.dependencies import get_projects_provider

router = APIRouter()


@router.get("/", response_model=list[Project])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    status: ProjectStatus | None = None,
    projects_provider: InMemoryProvider[Project, UUID] = Depends(get_projects_provider),
):
    projects = await projects_provider.list(skip=skip, limit=limit)

    if status:
        projects = [p for p in projects if p.status == status]

    return projects


@router.post("/", response_model=Project)
async def create_project(
    project: ProjectCreate,
    projects_provider: InMemoryProvider[Project, UUID] = Depends(get_projects_provider),
):
    return await projects_provider.create(project)


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: UUID,
    projects_provider: InMemoryProvider[Project, UUID] = Depends(get_projects_provider),
):
    project = await projects_provider.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: UUID,
    project: ProjectCreate,
    projects_provider: InMemoryProvider[Project, UUID] = Depends(get_projects_provider),
):
    db_project = await projects_provider.get(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    updated_project = await projects_provider.update(project_id, project)
    return updated_project


@router.delete("/{project_id}", response_model=bool)
async def delete_project(
    project_id: UUID,
    projects_provider: InMemoryProvider[Project, UUID] = Depends(get_projects_provider),
):
    db_project = await projects_provider.get(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await projects_provider.delete(project_id)

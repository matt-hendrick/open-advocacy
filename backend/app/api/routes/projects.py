from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID

from app.models.pydantic.models import Project, ProjectBase, ProjectStatus, Jurisdiction
from app.db.base import DatabaseProvider
from app.db.dependencies import (
    get_projects_provider,
    get_status_records_provider,
    get_groups_provider,
    get_jurisdictions_provider,
)
from app.utils.status import calculate_status_distribution

router = APIRouter()


# TODO: Add auth to get user and get group
@router.get("/", response_model=list[Project])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    status: ProjectStatus | None = None,
    group_id: UUID | None = None,
    projects_provider: DatabaseProvider = Depends(get_projects_provider),
    status_records_provider: DatabaseProvider = Depends(get_status_records_provider),
):
    """List projects with optional filtering."""
    filters = {}
    if status:
        filters["status"] = status.value
    if group_id:
        filters["group_id"] = group_id

    if filters:
        projects = await projects_provider.filter(**filters)
    else:
        projects = await projects_provider.list(skip=skip, limit=limit)

    # Add status distribution data
    if projects:
        status_records = await status_records_provider.list()
        for project in projects:
            project_records = [
                sr for sr in status_records if sr.project_id == project.id
            ]
            project.status_distribution = calculate_status_distribution(project_records)

    return projects


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectBase,
    projects_provider: DatabaseProvider = Depends(get_projects_provider),
    groups_provider: DatabaseProvider = Depends(get_groups_provider),
):
    """Create a new project."""
    # Verify group exists if provided
    if project.group_id:
        group = await groups_provider.get(project.group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
            )

    return await projects_provider.create(project)


# TODO: Add group filtering
@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: UUID,
    projects_provider: DatabaseProvider[Project, UUID] = Depends(get_projects_provider),
    status_records_provider: DatabaseProvider = Depends(get_status_records_provider),
    jurisdictions_provider: DatabaseProvider = Depends(get_jurisdictions_provider),
):
    project = await projects_provider.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Calculate status distribution
    status_records = await status_records_provider.list()
    project_status_records = [
        sr for sr in status_records if sr.project_id == project_id
    ]
    project.status_distribution = calculate_status_distribution(project_status_records)
    
    jurisdiction_id = project.jurisdiction_id
    jurisdiction : Jurisdiction = await jurisdictions_provider.get(jurisdiction_id)
    if jurisdiction and jurisdiction.name:
        project.jurisdiction_name = jurisdiction.name

    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: UUID,
    project: ProjectBase,
    projects_provider: DatabaseProvider[Project, UUID] = Depends(get_projects_provider),
):
    db_project = await projects_provider.get(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    updated_project = await projects_provider.update(project_id, project)
    return updated_project


@router.delete("/{project_id}", response_model=bool)
async def delete_project(
    project_id: UUID,
    projects_provider: DatabaseProvider[Project, UUID] = Depends(get_projects_provider),
):
    db_project = await projects_provider.get(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await projects_provider.delete(project_id)

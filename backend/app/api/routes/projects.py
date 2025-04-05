from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID

from app.models.pydantic.models import Project, ProjectBase, ProjectStatus
from app.db.base import DatabaseProvider
from app.db.dependencies import (
    get_projects_provider,
    get_status_records_provider,
    get_groups_provider,
    get_jurisdictions_provider,
    get_entities_provider,
)
from app.utils.project import (
    get_project_status_distribution,
    enrich_projects_with_status_distributions,
    enrich_projects_with_jurisdiction_name,
)

router = APIRouter()


@router.get("/", response_model=list[Project])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    status: ProjectStatus = None,
    group_id: UUID = None,
    projects_provider: DatabaseProvider = Depends(get_projects_provider),
    status_records_provider: DatabaseProvider = Depends(get_status_records_provider),
    entities_provider: DatabaseProvider = Depends(get_entities_provider),
    jurisdictions_provider: DatabaseProvider = Depends(get_jurisdictions_provider),
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

    # TODO: Clean up the logic between this and the get endpoint
    # Add status distribution/jurisdiction name data
    if projects:
        projects = await enrich_projects_with_status_distributions(
            projects=projects,
            status_records_provider=status_records_provider,
            entities_provider=entities_provider,
        )
        projects = await enrich_projects_with_jurisdiction_name(
            projects=projects, jurisdictions_provider=jurisdictions_provider
        )

    return projects


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectBase,
    projects_provider: DatabaseProvider = Depends(get_projects_provider),
    groups_provider: DatabaseProvider = Depends(get_groups_provider),
    jurisdictions_provider: DatabaseProvider = Depends(get_jurisdictions_provider),
):
    """Create a new project."""
    # Verify group exists if provided
    if project.group_id:
        group = await groups_provider.get(project.group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
            )
    # Valid jurisdiction
    if project.jurisdiction_id:
        jurisdiction = await jurisdictions_provider.get(project.jurisdiction_id)
        if not jurisdiction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Jurisdiction not found"
            )

    return await projects_provider.create(project)


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: UUID,
    projects_provider: DatabaseProvider = Depends(get_projects_provider),
    status_records_provider: DatabaseProvider = Depends(get_status_records_provider),
    jurisdictions_provider: DatabaseProvider = Depends(get_jurisdictions_provider),
    entities_provider: DatabaseProvider = Depends(get_entities_provider),
):
    """Get a project by ID with related jurisdiction and status information."""
    # Get the project
    project = await projects_provider.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # TODO: Clean up the logic between this and the list endpoint
    # Get jurisdiction name
    jurisdiction_id = project.jurisdiction_id
    jurisdiction = await jurisdictions_provider.get(jurisdiction_id)
    if jurisdiction and jurisdiction.name:
        project.jurisdiction_name = jurisdiction.name

    # Get status distribution
    project.status_distribution = await get_project_status_distribution(
        project_id=project_id,
        project=project,
        status_records_provider=status_records_provider,
        entities_provider=entities_provider,
    )

    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: UUID,
    project: ProjectBase,
    projects_provider: DatabaseProvider = Depends(get_projects_provider),
    groups_provider: DatabaseProvider = Depends(get_groups_provider),
    jurisdictions_provider: DatabaseProvider = Depends(get_jurisdictions_provider),
):
    db_project = await projects_provider.get(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify group exists if provided
    if project.group_id:
        group = await groups_provider.get(project.group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
            )
    # Valid jurisdiction
    if project.jurisdiction_id:
        jurisdiction = await jurisdictions_provider.get(project.jurisdiction_id)
        if not jurisdiction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Jurisdiction not found"
            )

    updated_project = await projects_provider.update(project_id, project)
    return updated_project


@router.delete("/{project_id}", response_model=bool)
async def delete_project(
    project_id: UUID,
    projects_provider: DatabaseProvider = Depends(get_projects_provider),
):
    db_project = await projects_provider.get(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await projects_provider.delete(project_id)

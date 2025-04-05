from uuid import UUID
from typing import List, Optional

from app.models.pydantic.models import Project, StatusDistribution
from app.db.base import DatabaseProvider
from app.utils.status import calculate_status_distribution


async def get_project_status_distribution(
    project_id: UUID,
    project: Optional[Project] = None,
    projects_provider: Optional[DatabaseProvider] = None,
    status_records_provider: DatabaseProvider = None,
    entities_provider: DatabaseProvider = None,
) -> StatusDistribution:
    """
    Get status distribution for a project, filtered by entities in the project's jurisdiction.

    Args:
        project_id: UUID of the project
        project: Optional Project object (to avoid fetching it again)
        projects_provider: Provider for projects
        status_records_provider: Provider for status records
        entities_provider: Provider for entities

    Returns:
        StatusDistribution object
    """
    # Get project if not provided
    if not project and projects_provider:
        project = await projects_provider.get(project_id)
        if not project:
            return (
                StatusDistribution()
            )  # Return empty distribution if project not found

    if not project:
        return StatusDistribution()  # Return empty distribution if project not provided

    # Get entities for the project's jurisdiction
    jurisdiction_id = project.jurisdiction_id
    jurisdiction_entities = await entities_provider.filter(
        jurisdiction_id=jurisdiction_id
    )
    entity_ids = [entity.id for entity in jurisdiction_entities]

    if not entity_ids:
        return StatusDistribution()  # Return empty distribution if no entities

    # Get status records for the project and these entities using IN filter
    try:
        project_status_records = await status_records_provider.filter_multiple(
            filters={"project_id": project_id}, in_filters={"entity_id": entity_ids}
        )
    except (AttributeError, NotImplementedError):
        # Fallback to the older approach if filter_multiple is not available on provider
        all_status_records = await status_records_provider.list()
        project_status_records = [
            sr
            for sr in all_status_records
            if sr.project_id == project_id and sr.entity_id in entity_ids
        ]

    return calculate_status_distribution(project_status_records)


async def enrich_projects_with_status_distributions(
    projects: List[Project],
    status_records_provider: DatabaseProvider,
    entities_provider: DatabaseProvider,
) -> List[Project]:
    """
    Enrich a list of projects with their status distributions.

    Args:
        projects: List of Project objects
        status_records_provider: Provider for status records
        entities_provider: Provider for entities

    Returns:
        List of Project objects with status_distribution field populated
    """
    if not projects:
        return []

    for project in projects:
        project.status_distribution = await get_project_status_distribution(
            project_id=project.id,
            project=project,
            status_records_provider=status_records_provider,
            entities_provider=entities_provider,
        )

    return projects

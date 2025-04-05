from app.models.pydantic.models import (
    EntityStatusRecord,
    StatusDistribution,
    EntityStatus,
)
from typing import List, Dict
from uuid import UUID


def calculate_status_distribution_with_neutrals(
    status_records: List[EntityStatusRecord], total_entity_count: int
) -> StatusDistribution:
    """
    Calculate the distribution of statuses for a list of entity status records,
    accounting for all entities in a jurisdiction (including those without explicit status).

    Args:
        status_records: List of status records for the project
        total_entity_count: Total number of entities in the jurisdiction

    Returns:
        StatusDistribution object
    """
    # Initialize all entities as neutral
    distribution = StatusDistribution(
        neutral=total_entity_count,  # Start with all entities as NEUTRAL
        total=total_entity_count,  # Total equals all entities in jurisdiction
    )

    # Create a mapping of entity_id to status for faster lookup
    entity_statuses: Dict[UUID, EntityStatus] = {
        record.entity_id: record.status for record in status_records
    }

    # Process explicit status records
    for entity_id, status in entity_statuses.items():
        if status == EntityStatus.NEUTRAL:
            continue  # Already counted as neutral

        # Decrement the neutral count for non-neutral statuses
        distribution.neutral -= 1

        # Increment the appropriate status count
        if status == EntityStatus.SOLID_APPROVAL:
            distribution.solid_approval += 1
        elif status == EntityStatus.LEANING_APPROVAL:
            distribution.leaning_approval += 1
        elif status == EntityStatus.LEANING_DISAPPROVAL:
            distribution.leaning_disapproval += 1
        elif status == EntityStatus.SOLID_DISAPPROVAL:
            distribution.solid_disapproval += 1
        else:
            distribution.unknown += 1

    return distribution

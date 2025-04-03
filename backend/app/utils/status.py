from app.models.pydantic.models import (
    EntityStatusRecord,
    StatusDistribution,
    EntityStatus,
)


def calculate_status_distribution(
    status_records: list[EntityStatusRecord],
) -> StatusDistribution:
    """Calculate the distribution of statuses for a list of entity status records."""
    distribution = StatusDistribution()

    for record in status_records:
        distribution.total += 1
        if record.status == EntityStatus.SOLID_APPROVAL:
            distribution.solid_approval += 1
        elif record.status == EntityStatus.LEANING_APPROVAL:
            distribution.leaning_approval += 1
        elif record.status == EntityStatus.NEUTRAL:
            distribution.neutral += 1
        elif record.status == EntityStatus.LEANING_DISAPPROVAL:
            distribution.leaning_disapproval += 1
        elif record.status == EntityStatus.SOLID_DISAPPROVAL:
            distribution.solid_disapproval += 1
        else:
            distribution.unknown += 1

    return distribution

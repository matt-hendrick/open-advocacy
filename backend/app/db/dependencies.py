from app.db.base import InMemoryProvider
from app.models.pydantic.models import (
    Project,
    Group,
    Entity,
    EntityStatusRecord,
    Jurisdiction,
)
from uuid import UUID

# Global providers
project_provider = InMemoryProvider[Project, UUID](Project)
group_provider = InMemoryProvider[Group, UUID](Group)
entity_provider = InMemoryProvider[Entity, UUID](Entity)
status_records_provider = InMemoryProvider[EntityStatusRecord, UUID](EntityStatusRecord)
jurisdictions_provider = InMemoryProvider[Jurisdiction, UUID](Jurisdiction)


# Dependency functions
def get_projects_provider():
    return project_provider


def get_groups_provider():
    return group_provider


def get_entities_provider():
    return entity_provider


def get_status_records_provider():
    return status_records_provider


def get_jurisdictions_provider():
    return jurisdictions_provider

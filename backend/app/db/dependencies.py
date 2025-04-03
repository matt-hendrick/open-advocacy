from app.db.base import InMemoryProvider
from app.models.pydantic.models import Project, Group, Entity
from uuid import UUID

# Global providers - would likely be initialized at startup
project_provider = InMemoryProvider[Project, UUID](Project)
group_provider = InMemoryProvider[Group, UUID](Group)
entity_provider = InMemoryProvider[Entity, UUID](Entity)


# Dependency functions to get providers
def get_projects_provider():
    return project_provider


def get_groups_provider():
    return group_provider


def get_entities_provider():
    return entity_provider

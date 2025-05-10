from app.db.provider_factory import ProviderFactory
from app.models.pydantic.models import (
    Project,
    Group,
    Entity,
    EntityStatusRecord,
    Jurisdiction,
    District,
    User,
)
from app.models.orm import models as orm_models


def get_projects_provider():
    return ProviderFactory.get_provider(
        pydantic_model=Project, orm_model=orm_models.Project
    )


def get_groups_provider():
    return ProviderFactory.get_provider(
        pydantic_model=Group, orm_model=orm_models.Group
    )


def get_entities_provider():
    return ProviderFactory.get_provider(
        pydantic_model=Entity, orm_model=orm_models.Entity
    )


def get_status_records_provider():
    return ProviderFactory.get_provider(
        pydantic_model=EntityStatusRecord, orm_model=orm_models.EntityStatusRecord
    )


def get_jurisdictions_provider():
    return ProviderFactory.get_provider(
        pydantic_model=Jurisdiction, orm_model=orm_models.Jurisdiction
    )


def get_districts_provider():
    return ProviderFactory.get_provider(
        pydantic_model=District, orm_model=orm_models.District
    )


def get_users_provider():
    return ProviderFactory.get_provider(pydantic_model=User, orm_model=orm_models.User)

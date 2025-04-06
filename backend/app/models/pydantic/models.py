from pydantic import BaseModel, Field, validator
import json
from typing import Any, Union
from enum import Enum
from datetime import datetime
from uuid import uuid4, UUID


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class EntityStatus(str, Enum):
    SOLID_APPROVAL = "solid_approval"
    LEANING_APPROVAL = "leaning_approval"
    NEUTRAL = "neutral"
    LEANING_DISAPPROVAL = "leaning_disapproval"
    SOLID_DISAPPROVAL = "solid_disapproval"


class EntityBase(BaseModel):
    name: str
    title: str | None = None
    entity_type: str  # e.g., "alderman", "state_rep", "mayor"
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    address: str | None = None
    jurisdiction_id: UUID
    district_id: UUID


class EntityCreate(EntityBase):
    jurisdiction_id: UUID


class Entity(EntityBase):
    id: UUID = Field(default_factory=uuid4)
    jurisdiction_name: str | None = None
    district_name: str | None = None

    class Config:
        from_attributes = True


class JurisdictionBase(BaseModel):
    name: str
    description: str | None = None
    level: str  # city, state, federal
    parent_jurisdiction_id: UUID | None = None


class Jurisdiction(JurisdictionBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class DistrictBase(BaseModel):
    name: str
    code: str | None = None
    jurisdiction_id: UUID


class District(DistrictBase):
    id: UUID = Field(default_factory=uuid4)
    boundary: Union[dict[str, Any], str] | None = None

    @validator("boundary")
    def parse_boundary(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return v
        return v

    class Config:
        from_attributes = True


class EntityStatusRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    entity_id: UUID
    project_id: UUID
    status: EntityStatus = EntityStatus.NEUTRAL
    notes: str | None = None
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: str

    class Config:
        from_attributes = True


class StatusDistribution(BaseModel):
    solid_approval: int = 0
    leaning_approval: int = 0
    neutral: int = 0
    leaning_disapproval: int = 0
    solid_disapproval: int = 0
    unknown: int = 0
    total: int = 0


class GroupBase(BaseModel):
    name: str
    description: str | None = None


class Group(GroupBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    title: str
    description: str | None = None
    status: ProjectStatus = ProjectStatus.DRAFT
    active: bool = True
    link: str | None = None
    preferred_status: EntityStatus = EntityStatus.SOLID_APPROVAL
    template_response: str | None = None
    jurisdiction_id: UUID | None = None
    group_id: UUID | None = None


class Project(ProjectBase):
    id: UUID = Field(default_factory=uuid4)
    created_by: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status_distribution: StatusDistribution | None = None
    jurisdiction_name: str | None = None

    class Config:
        from_attributes = True


class AddressLookupRequest(BaseModel):
    address: str

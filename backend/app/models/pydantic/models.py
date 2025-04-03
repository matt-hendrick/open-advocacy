from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from uuid import uuid4, UUID


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class GroupStance(str, Enum):
    PRO = "pro"
    CON = "con"
    NEUTRAL = "neutral"


class GroupBase(BaseModel):
    name: str
    description: str | None = None
    stance: GroupStance = GroupStance.NEUTRAL


class GroupCreate(GroupBase):
    project_id: UUID


class Group(GroupBase):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    title: str
    description: str | None = None
    status: ProjectStatus = ProjectStatus.DRAFT
    active: bool = True


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: UUID = Field(default_factory=uuid4)
    created_by: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    vote_count: int = 0
    groups: list[Group] = []

    class Config:
        from_attributes = True


class ContactInfo(BaseModel):
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    address: str | None = None


class EntityBase(BaseModel):
    name: str
    title: str | None = None
    entity_type: str  # e.g., "alderman", "state_rep", "mayor"
    contact_info: ContactInfo = Field(default_factory=ContactInfo)


class EntityCreate(EntityBase):
    jurisdiction_id: str
    location_module_id: str = "default"


class Entity(EntityBase):
    id: UUID = Field(default_factory=uuid4)
    jurisdiction_id: str
    location_module_id: str = "default"

    class Config:
        from_attributes = True


class AddressLookupRequest(BaseModel):
    address: str

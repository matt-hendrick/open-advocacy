import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="group")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    active = Column(Boolean, default=True)
    link = Column(String(255), nullable=True)
    preferred_status = Column(String(50), nullable=False, default="solid_approval")
    template_response = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    vote_count = Column(Integer, default=0)
    jurisdiction_id = Column(
        UUID(as_uuid=True), ForeignKey("jurisdictions.id"), nullable=True
    )
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)

    # Relationships
    status_records = relationship("EntityStatusRecord", back_populates="project")
    jurisdiction = relationship("Jurisdiction", back_populates="projects")
    group = relationship("Group", back_populates="projects")


class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(String(50), nullable=False)  # city, state, federal
    parent_jurisdiction_id = Column(
        UUID(as_uuid=True), ForeignKey("jurisdictions.id"), nullable=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    entities = relationship("Entity", back_populates="jurisdiction")
    parent = relationship("Jurisdiction", remote_side=[id], back_populates="children")
    children = relationship("Jurisdiction", back_populates="parent")
    projects = relationship("Project", back_populates="jurisdiction")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    entity_type = Column(String(50), nullable=False)
    jurisdiction_id = Column(
        UUID(as_uuid=True), ForeignKey("jurisdictions.id"), nullable=False
    )
    location_module_id = Column(String(50), nullable=False, default="default")
    district = Column(String(255), nullable=True)

    # Contact info fields
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)

    # Relationships
    jurisdiction = relationship("Jurisdiction", back_populates="entities")
    status_records = relationship("EntityStatusRecord", back_populates="entity")


class EntityStatusRecord(Base):
    __tablename__ = "entity_status_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    status = Column(String(50), nullable=False, default="neutral")
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(255), nullable=False)

    # Relationships
    entity = relationship("Entity", back_populates="status_records")
    project = relationship("Project", back_populates="status_records")

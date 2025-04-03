// src/utils/dataTransformers.ts
import { Project, Entity, ProjectStatus } from '../types';

export const transformProjectFromApi = (project: any): Project => {
  return {
    id: project.id,
    title: project.title,
    description: project.description || '',
    status: project.status as ProjectStatus,
    active: project.active,
    created_by: project.created_by || '',
    created_at: project.created_at,
    updated_at: project.updated_at,
    vote_count: project.vote_count,
    groups: project.groups || [],
  };
};

export const transformEntityFromApi = (entity: any): Entity => {
  return {
    id: entity.id,
    name: entity.name,
    title: entity.title || '',
    entity_type: entity.entity_type,
    contact_info: {
      email: entity.contact_info?.email || '',
      phone: entity.contact_info?.phone || '',
      website: entity.contact_info?.website || '',
      address: entity.contact_info?.address || '',
    },
    jurisdiction_id: entity.jurisdiction_id,
    location_module_id: entity.location_module_id || 'default',
  };
};

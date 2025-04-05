import { Project, Entity, EntityStatus, ProjectStatus, Group } from '../types';

export const transformProjectFromApi = (project: any): Project => {
  return {
    id: project.id,
    title: project.title,
    description: project.description || '',
    status: project.status as ProjectStatus,
    active: project.active,
    link: project.link || '',
    preferred_status: project.preferred_status || EntityStatus.SOLID_APPROVAL,
    template_response: project.template_response || '',
    jurisdiction_id: project.jurisdiction_id,
    jurisdiction_name: project.jurisdiction_name,
    group_id: project.group_id,
    created_by: project.created_by || '',
    created_at: project.created_at,
    updated_at: project.updated_at,
    status_distribution: project.status_distribution || {
      solid_approval: 0,
      leaning_approval: 0,
      neutral: 0,
      leaning_disapproval: 0,
      solid_disapproval: 0,
      unknown: 0,
      total: 0,
    },
  };
};

export const transformGroupFromApi = (group: any): Group => {
  return {
    id: group.id,
    name: group.name,
    description: group.description || '',
    created_at: group.created_at,
  };
};

export const transformEntityFromApi = (entity: any): Entity => {
  return {
    id: entity.id,
    name: entity.name,
    title: entity.title || '',
    entity_type: entity.entity_type,
    email: entity.email || '',
    phone: entity.phone || '',
    website: entity.website || '',
    address: entity.address || '',
    district: entity.district || '',
    jurisdiction_id: entity.jurisdiction_id,
    location_module_id: entity.location_module_id || 'default',
  };
};

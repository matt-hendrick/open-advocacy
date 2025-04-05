export enum ProjectStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

export enum EntityStatus {
  SOLID_APPROVAL = 'solid_approval',
  LEANING_APPROVAL = 'leaning_approval',
  NEUTRAL = 'neutral',
  LEANING_DISAPPROVAL = 'leaning_disapproval',
  SOLID_DISAPPROVAL = 'solid_disapproval',
}

export enum GroupStance {
  PRO = 'pro',
  CON = 'con',
  NEUTRAL = 'neutral',
}

export interface ContactInfo {
  email?: string;
  phone?: string;
  website?: string;
  address?: string;
}

export interface Jurisdiction {
  id: string;
  name: string;
  description?: string;
  level: string; // city, state, federal
  parent_jurisdiction_id?: string;
  created_at: string;
}

export interface Entity {
  id: string;
  name: string;
  title?: string;
  entity_type: string;
  contact_info: ContactInfo;
  jurisdiction_id: string;
  location_module_id: string;
}

export interface EntityStatusRecord {
  id: string;
  entity_id: string;
  project_id: string;
  status: EntityStatus;
  notes?: string;
  updated_at: string;
  updated_by: string;
}

export interface StatusDistribution {
  solid_approval: number;
  leaning_approval: number;
  neutral: number;
  leaning_disapproval: number;
  solid_disapproval: number;
  unknown: number;
  total: number;
}

export interface Project {
  id: string;
  title: string;
  description?: string;
  status: ProjectStatus;
  active: boolean;
  link?: string;
  preferred_status: EntityStatus;
  template_response?: string;
  jurisdiction_id: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
  groups?: Group[];
  status_distribution?: StatusDistribution;
}

export interface Group {
  id: string;
  name: string;
  description?: string;
  stance: GroupStance;
  project_id: string;
  created_at: string;
}

export interface AddressLookupRequest {
  address: string;
}

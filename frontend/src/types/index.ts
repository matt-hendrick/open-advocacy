export enum ProjectStatus {
    DRAFT = "draft",
    ACTIVE = "active",
    COMPLETED = "completed",
    ARCHIVED = "archived"
  }
  
  export enum GroupStance {
    PRO = "pro",
    CON = "con",
    NEUTRAL = "neutral"
  }
  
  export interface ContactInfo {
    email?: string;
    phone?: string;
    website?: string;
    address?: string;
  }
  
  export interface Project {
    id: string;
    title: string;
    description?: string;
    status: ProjectStatus;
    active: boolean;
    created_by?: string;
    created_at: string;
    updated_at: string;
    vote_count: number;
    groups?: Group[];
  }
  
  export interface Group {
    id: string;
    name: string;
    description?: string;
    stance: GroupStance;
    project_id: string;
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
  
  export interface AddressLookupRequest {
    address: string;
  }
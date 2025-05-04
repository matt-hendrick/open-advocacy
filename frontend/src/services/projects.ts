import api from './api';
import { Project, ProjectStatus, EntityStatus } from '../types';

interface ProjectCreateData {
  title: string;
  description?: string;
  status?: ProjectStatus;
  active?: boolean;
  link?: string;
  preferred_status?: EntityStatus;
  template_response?: string;
  jurisdiction_id?: string;
  group_id?: string;
}

interface ProjectFilterParams {
  status?: ProjectStatus;
  group_id?: string;
  skip?: number;
  limit?: number;
  include_archived?: boolean;
}

export const projectService = {
  async getProjects(filters?: ProjectFilterParams): Promise<{ data: Project[] }> {
    const queryParams = new URLSearchParams();

    if (filters) {
      if (filters.status) {
        queryParams.append('status', filters.status);
      }

      if (filters.group_id) {
        queryParams.append('group_id', filters.group_id);
      }

      // TODO: Implement pagination
      if (filters.skip !== undefined) {
        queryParams.append('skip', filters.skip.toString());
      }

      if (filters.limit !== undefined) {
        queryParams.append('limit', filters.limit.toString());
      }
    }

    const queryString = queryParams.toString();
    const url = `/projects/${queryString ? `?${queryString}` : ''}`;

    return api.get<Project[]>(url);
  },

  async getProject(id: string): Promise<{ data: Project }> {
    return api.get<Project>(`/projects/${id}`);
  },

  async createProject(project: ProjectCreateData): Promise<{ data: Project }> {
    return api.post<Project>('/projects/', {
      ...project,
      preferred_status: project.preferred_status || EntityStatus.SOLID_APPROVAL,
    });
  },

  async updateProject(id: string, project: ProjectCreateData): Promise<{ data: Project }> {
    return api.put<Project>(`/projects/${id}`, project);
  },

  async deleteProject(id: string): Promise<{ data: boolean }> {
    return api.delete<boolean>(`/projects/${id}`);
  },
};

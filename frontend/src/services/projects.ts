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

export const projectService = {
  async getProjects(groupId?: string): Promise<{ data: Project[] }> {
    const params = groupId ? `?group_id=${groupId}` : '';
    return api.get<Project[]>(`/projects${params}`);
  },

  async getProject(id: string): Promise<{ data: Project }> {
    return api.get<Project>(`/projects/${id}`);
  },

  async createProject(project: ProjectCreateData): Promise<{ data: Project }> {
    return api.post<Project>('/projects', {
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
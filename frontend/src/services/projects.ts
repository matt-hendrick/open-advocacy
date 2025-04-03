import api from './api';
import { Project, ProjectStatus } from '../types';

interface ProjectCreateData {
  title: string;
  description?: string;
  status?: ProjectStatus;
  active?: boolean;
}

export const projectService = {
  async getProjects(): Promise<{ data: Project[] }> {
    return api.get<Project[]>('/projects');
  },

  async getProject(id: string): Promise<{ data: Project }> {
    return api.get<Project>(`/projects/${id}`);
  },

  async createProject(project: ProjectCreateData): Promise<{ data: Project }> {
    return api.post<Project>('/projects', project);
  },

  async updateProject(id: string, project: ProjectCreateData): Promise<{ data: Project }> {
    return api.put<Project>(`/projects/${id}`, project);
  },

  async deleteProject(id: string): Promise<{ data: boolean }> {
    return api.delete<boolean>(`/projects/${id}`);
  },
};

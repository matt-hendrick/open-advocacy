import api from './api';
import { mockProjects } from '../data/projects';
import { Project, ProjectStatus } from '../types';

// Flag to use mock data during development
const USE_MOCK_DATA = true;

interface ProjectCreateData {
  title: string;
  description?: string;
  status?: ProjectStatus;
  active?: boolean;
}

export const projectService = {
  async getProjects(): Promise<{ data: Project[] }> {
    if (USE_MOCK_DATA) {
      return Promise.resolve({ data: mockProjects });
    }
    return api.get<Project[]>('/projects');
  },

  async getProject(id: string): Promise<{ data: Project | undefined }> {
    if (USE_MOCK_DATA) {
      const project = mockProjects.find(p => p.id === id);
      return Promise.resolve({ data: project });
    }
    return api.get<Project>(`/projects/${id}`);
  },

  async createProject(project: ProjectCreateData): Promise<{ data: Project }> {
    if (USE_MOCK_DATA) {
      // Simulate a server response
      return Promise.resolve({ 
        data: { 
          ...project, 
          id: Math.random().toString(36).substring(2, 15),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          vote_count: 0,
          status: project.status || ProjectStatus.DRAFT,
          active: project.active ?? true,
        } as Project 
      });
    }
    return api.post<Project>('/projects', project);
  },

  async updateProject(id: string, project: ProjectCreateData): Promise<{ data: Project }> {
    if (USE_MOCK_DATA) {
      // Simulate a server response
      return Promise.resolve({ 
        data: { 
          ...project, 
          id, 
          updated_at: new Date().toISOString(),
          status: project.status || ProjectStatus.DRAFT,
          active: project.active ?? true,
          created_at: new Date().toISOString(),
          vote_count: 0
        } as Project 
      });
    }
    return api.put<Project>(`/projects/${id}`, project);
  },

  async deleteProject(id: string): Promise<{ data: boolean }> {
    if (USE_MOCK_DATA) {
      return Promise.resolve({ data: true });
    }
    return api.delete<boolean>(`/projects/${id}`);
  }
};
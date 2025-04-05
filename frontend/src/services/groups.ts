import api from './api';
import { Group } from '../types';

interface GroupCreateData {
  name: string;
  description?: string;
}

export const groupService = {
  async getGroups(): Promise<{ data: Group[] }> {
    return api.get<Group[]>('/groups');
  },

  async getGroup(id: string): Promise<{ data: Group }> {
    return api.get<Group>(`/groups/${id}`);
  },

  async createGroup(group: GroupCreateData): Promise<{ data: Group }> {
    return api.post<Group>('/groups', group);
  },

  async updateGroup(id: string, group: GroupCreateData): Promise<{ data: Group }> {
    return api.put<Group>(`/groups/${id}`, group);
  },

  async deleteGroup(id: string): Promise<{ data: boolean }> {
    return api.delete<boolean>(`/groups/${id}`);
  },
};

import api from './api';
import { EntityStatusRecord, EntityStatus } from '../types';

interface StatusCreateData {
  entity_id: string;
  project_id: string;
  status: EntityStatus;
  notes?: string;
  updated_by: string;
}

export const statusService = {
  async getStatusRecords(
    projectId?: string,
    entityId?: string
  ): Promise<{ data: EntityStatusRecord[] }> {
    let url = '/status';
    const params = [];

    if (projectId) params.push(`project_id=${projectId}`);
    if (entityId) params.push(`entity_id=${entityId}`);

    if (params.length > 0) {
      url += `?${params.join('&')}`;
    }

    return api.get<EntityStatusRecord[]>(url);
  },

  async getStatusRecord(id: string): Promise<{ data: EntityStatusRecord }> {
    return api.get<EntityStatusRecord>(`/status/${id}`);
  },

  async createStatusRecord(data: StatusCreateData): Promise<{ data: EntityStatusRecord }> {
    return api.post<EntityStatusRecord>('/status', {
      ...data,
      updated_at: new Date().toISOString(),
    });
  },

  async updateStatusRecord(
    id: string,
    data: Partial<StatusCreateData>
  ): Promise<{ data: EntityStatusRecord }> {
    return api.put<EntityStatusRecord>(`/status/${id}`, {
      ...data,
      updated_at: new Date().toISOString(),
    });
  },

  async deleteStatusRecord(id: string): Promise<{ data: boolean }> {
    return api.delete<boolean>(`/status/${id}`);
  },
};

import api from './api';
import { Entity } from '../types';

export const representativeService = {
  async findByAddress(address: string, moduleId: string = 'default'): Promise<{ data: Entity[] }> {
    return api.post<Entity[]>(`/location/lookup?module_id=${moduleId}`, { address });
  },

  async getAvailableModules(): Promise<{ data: Record<string, string> }> {
    return api.get<Record<string, string>>('/location/modules');
  },

  async getEntityTypes(moduleId: string = 'default'): Promise<{ data: string[] }> {
    return api.get<string[]>(`/location/entity-types?module_id=${moduleId}`);
  },
};

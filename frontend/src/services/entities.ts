import api from './api';
import { Entity } from '../types';

export const entityService = {
  async getEntitiesByJurisdictions(jurisdictionIds: string[]): Promise<{ data: Entity[] }> {
    const params = new URLSearchParams();

    // Add each ID as a separate parameter with the same name
    jurisdictionIds.forEach(id => {
      params.append('jurisdiction_ids', id);
    });

    return api.get<Entity[]>(`/entities/by-jurisdictions?${params.toString()}`);
  },
};

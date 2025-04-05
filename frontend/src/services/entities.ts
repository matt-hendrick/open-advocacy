import api from './api';
import { Entity } from '../types';

export const entityService = {
  async getEntitiesByJurisdictions(jurisdictionId: string): Promise<{ data: Entity[] }> {
    return api.get<Entity[]>(`/entities/by-jurisdictions?jurisdiction_id=${jurisdictionId}`);
  },
};

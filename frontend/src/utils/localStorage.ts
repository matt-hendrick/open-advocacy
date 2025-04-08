import { Entity } from '../types';

const STORAGE_KEYS = {
  REPRESENTATIVES: 'openAdvocacy_userRepresentatives',
  ADDRESS: 'openAdvocacy_userAddress',
  DISTRICTS: 'openAdvocacy_userDistricts',
};

export interface RepresentativeStorage {
  representatives: Entity[];
  address: string;
  districts: string[];
}

export const representativeStorage = {
  saveRepresentativeData: (data: RepresentativeStorage): void => {
    try {
      localStorage.setItem(STORAGE_KEYS.REPRESENTATIVES, JSON.stringify(data.representatives));
      localStorage.setItem(STORAGE_KEYS.ADDRESS, data.address);
      localStorage.setItem(STORAGE_KEYS.DISTRICTS, JSON.stringify(data.districts));
    } catch (error) {
      console.error('Error saving representative data to storage:', error);
    }
  },

  loadRepresentativeData: (): RepresentativeStorage => {
    try {
      const savedReps = localStorage.getItem(STORAGE_KEYS.REPRESENTATIVES);
      const savedAddress = localStorage.getItem(STORAGE_KEYS.ADDRESS);
      const savedDistricts = localStorage.getItem(STORAGE_KEYS.DISTRICTS);

      return {
        representatives: savedReps ? JSON.parse(savedReps) : [],
        address: savedAddress || '',
        districts: savedDistricts ? JSON.parse(savedDistricts) : [],
      };
    } catch (error) {
      console.error('Error loading representative data from storage:', error);
      return { representatives: [], address: '', districts: [] };
    }
  },

  clearRepresentativeData: (): void => {
    try {
      localStorage.removeItem(STORAGE_KEYS.REPRESENTATIVES);
      localStorage.removeItem(STORAGE_KEYS.ADDRESS);
      localStorage.removeItem(STORAGE_KEYS.DISTRICTS);
    } catch (error) {
      console.error('Error clearing representative data from storage:', error);
    }
  },
};

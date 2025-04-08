import { EntityStatus } from '../types';

export const getStatusColor = (status: EntityStatus): string => {
  switch (status) {
    case EntityStatus.SOLID_APPROVAL:
      return '#2e7d32'; // Dark green
    case EntityStatus.LEANING_APPROVAL:
      return '#66bb6a'; // Light green
    case EntityStatus.NEUTRAL:
      return '#ffb74d'; // Orange
    case EntityStatus.LEANING_DISAPPROVAL:
      return '#ef5350'; // Light red
    case EntityStatus.SOLID_DISAPPROVAL:
      return '#c62828'; // Dark red
    default:
      return '#9e9e9e'; // Grey
  }
};

export const getStatusLabel = (status: EntityStatus): string => {
  switch (status) {
    case EntityStatus.SOLID_APPROVAL:
      return 'Solid Approval';
    case EntityStatus.LEANING_APPROVAL:
      return 'Leaning Approval';
    case EntityStatus.NEUTRAL:
      return 'Neutral';
    case EntityStatus.LEANING_DISAPPROVAL:
      return 'Leaning Disapproval';
    case EntityStatus.SOLID_DISAPPROVAL:
      return 'Solid Disapproval';
    default:
      return 'Unknown';
  }
};

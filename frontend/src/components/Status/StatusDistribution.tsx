import React from 'react';
import { Box, Typography, Tooltip } from '@mui/material';
import { StatusDistribution as StatusDistributionType, EntityStatus } from '../../types';

interface StatusBarProps {
  distribution: StatusDistributionType;
  size?: 'small' | 'medium' | 'large';
  showLabels?: boolean;
  showPercentages?: boolean;
}

const getStatusColor = (status: EntityStatus): string => {
  switch (status) {
    case EntityStatus.SOLID_APPROVAL:
      return '#2e7d32'; // Green
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

const getStatusTooltip = (status: EntityStatus): string => {
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

const StatusDistribution: React.FC<StatusBarProps> = ({
  distribution,
  size = 'medium',
  showLabels = false,
  showPercentages = false,
}) => {
  const total = distribution.total || 1; // Avoid division by zero

  const barHeight = size === 'small' ? 8 : size === 'medium' ? 16 : 24;
  const fontSize = size === 'small' ? 10 : size === 'medium' ? 12 : 14;

  const sections = [
    { status: EntityStatus.SOLID_APPROVAL, count: distribution.solid_approval },
    { status: EntityStatus.LEANING_APPROVAL, count: distribution.leaning_approval },
    { status: EntityStatus.NEUTRAL, count: distribution.neutral },
    { status: EntityStatus.LEANING_DISAPPROVAL, count: distribution.leaning_disapproval },
    { status: EntityStatus.SOLID_DISAPPROVAL, count: distribution.solid_disapproval },
    { status: 'unknown' as EntityStatus, count: distribution.unknown },
  ];

  return (
    <Box>
      {showLabels && (
        <Typography variant="subtitle2" gutterBottom>
          Status Distribution
        </Typography>
      )}

      <Box
        sx={{
          display: 'flex',
          width: '100%',
          height: barHeight,
          borderRadius: 1,
          overflow: 'hidden',
        }}
      >
        {sections.map((section, index) => {
          if (section.count === 0) return null;

          const percentage = (section.count / total) * 100;
          return (
            <Tooltip
              key={index}
              title={`${getStatusTooltip(section.status)}: ${section.count} (${percentage.toFixed(1)}%)`}
            >
              <Box
                sx={{
                  width: `${percentage}%`,
                  height: '100%',
                  backgroundColor: getStatusColor(section.status),
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  color: '#fff',
                  fontSize: fontSize,
                  fontWeight: 'bold',
                  minWidth: percentage < 8 ? 'auto' : 20,
                }}
              >
                {showPercentages && percentage >= 8 && `${Math.round(percentage)}%`}
              </Box>
            </Tooltip>
          );
        })}
      </Box>

      {distribution.total === 0 && (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
          No status data available
        </Typography>
      )}
    </Box>
  );
};

export default StatusDistribution;

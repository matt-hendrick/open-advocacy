// src/components/UserRepresentatives/UserRepresentativesProjectSection.tsx
import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Chip,
  Button,
  Divider,
  useTheme,
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import { useNavigate } from 'react-router-dom';
import { useUserRepresentatives } from '../../contexts/UserRepresentativesContext';
import { EntityStatus, Project, EntityStatusRecord } from '../../types';
import { getStatusColor, getStatusLabel } from '../../utils/statusColors';

interface UserRepresentativesProjectSectionProps {
  project: Project;
  statusRecords: EntityStatusRecord[];
}

const UserRepresentativesProjectSection: React.FC<UserRepresentativesProjectSectionProps> = ({
  project,
  statusRecords,
}) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { userRepresentatives, hasUserRepresentatives } = useUserRepresentatives();

  // Filter representatives that match the project jurisdiction
  const relevantReps = userRepresentatives.filter(
    rep => rep.jurisdiction_id === project.jurisdiction_id
  );

  // Create a map of entity ID to status record for quick lookups
  const statusMap = statusRecords.reduce(
    (acc, record) => {
      acc[record.entity_id] = record;
      return acc;
    },
    {} as Record<string, EntityStatusRecord>
  );

  if (!hasUserRepresentatives) {
    return (
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          Your Representatives
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Find your representatives to see where they stand on this project.
        </Typography>
        <Button
          variant="outlined"
          color="primary"
          size="small"
          onClick={() => navigate('/representatives')}
          sx={{ mt: 2 }}
        >
          Find Representatives
        </Button>
      </Paper>
    );
  }

  if (relevantReps.length === 0) {
    return (
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          Your Representatives
        </Typography>
        <Typography variant="body2" color="textSecondary">
          None of your saved representatives are involved with this project.
        </Typography>
        <Button
          variant="outlined"
          color="primary"
          size="small"
          onClick={() => navigate('/representatives')}
          sx={{ mt: 2 }}
        >
          Find More Representatives
        </Button>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Where Your Representatives Stand
      </Typography>

      <List>
        {relevantReps.map(rep => {
          const statusRecord = statusMap[rep.id];
          const status = statusRecord?.status || 'unknown';
          const notes = statusRecord?.notes;

          return (
            <ListItem
              key={rep.id}
              sx={{
                borderLeft: `4px solid ${getStatusColor(status)}`,
                mb: 1,
                backgroundColor: theme.palette.background.default,
                borderRadius: '0 4px 4px 0',
                display: 'block',
                padding: 2,
              }}
            >
              <Box display="flex" alignItems="center">
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
                    <PersonIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="subtitle1">{rep.name}</Typography>
                      <Chip
                        label={getStatusLabel(status)}
                        size="small"
                        sx={{
                          ml: 1,
                          backgroundColor: getStatusColor(status),
                          color: '#fff',
                        }}
                      />
                    </Box>
                  }
                  secondary={
                    <Typography variant="body2" color="textSecondary">
                      {rep.title} {rep.district_name ? `(${rep.district_name})` : ''}
                    </Typography>
                  }
                />
              </Box>

              {notes && (
                <Box
                  sx={{
                    ml: 9,
                    mt: 1,
                    p: 1.5,
                    backgroundColor: 'rgba(0,0,0,0.03)',
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="body2">{notes}</Typography>
                </Box>
              )}

              <Box sx={{ ml: 9, mt: 1.5 }}>
                <Button
                  variant="contained"
                  size="small"
                  color="primary"
                  onClick={() =>
                    navigate(`/contact?project=${project.id}&representative=${rep.id}`)
                  }
                >
                  Contact
                </Button>
              </Box>
            </ListItem>
          );
        })}
      </List>

      <Divider sx={{ my: 2 }} />

      <Button
        variant="outlined"
        fullWidth
        onClick={() => navigate(`/contact?project=${project.id}`)}
      >
        Contact All Your Representatives
      </Button>
    </Paper>
  );
};

export default UserRepresentativesProjectSection;

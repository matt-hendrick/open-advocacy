// src/components/Entity/EntityStatusManager.tsx
import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Divider,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Chip,
  Avatar,
  SelectChangeEvent,
  Link,
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import PublicIcon from '@mui/icons-material/Public';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { Entity, Project, EntityStatus, EntityStatusRecord } from '../../types';
import { statusService } from '../../services/status';

interface EntityStatusManagerProps {
  entity: Entity;
  project: Project;
  existingStatus?: EntityStatusRecord;
  onStatusUpdated?: () => void;
  isAdmin?: boolean;
}

const getStatusColor = (status: EntityStatus | undefined): string => {
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

const getStatusBgColor = (status: EntityStatus | undefined): string => {
  switch (status) {
    case EntityStatus.SOLID_APPROVAL:
      return 'rgba(46, 125, 50, 0.08)'; // Transparent green
    case EntityStatus.LEANING_APPROVAL:
      return 'rgba(102, 187, 106, 0.08)'; // Transparent light green
    case EntityStatus.NEUTRAL:
      return 'rgba(255, 183, 77, 0.08)'; // Transparent orange
    case EntityStatus.LEANING_DISAPPROVAL:
      return 'rgba(239, 83, 80, 0.08)'; // Transparent light red
    case EntityStatus.SOLID_DISAPPROVAL:
      return 'rgba(198, 40, 40, 0.08)'; // Transparent dark red
    default:
      return 'rgba(158, 158, 158, 0.08)'; // Transparent grey
  }
};

const getStatusLabel = (status: EntityStatus | undefined): string => {
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
      return 'No Status';
  }
};

const EntityStatusManager: React.FC<EntityStatusManagerProps> = ({
  entity,
  project,
  existingStatus,
  onStatusUpdated,
  isAdmin = false,
}) => {
  const [status, setStatus] = useState<EntityStatus>(
    existingStatus?.status || EntityStatus.NEUTRAL
  );
  const [notes, setNotes] = useState<string>(existingStatus?.notes || '');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleStatusChange = (event: SelectChangeEvent<EntityStatus>) => {
    setStatus(event.target.value as EntityStatus);
  };

  const handleNotesChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setNotes(event.target.value);
  };

  const handleSubmit = async () => {
    if (!isAdmin) return;

    setLoading(true);
    setError(null);

    try {
      if (existingStatus) {
        // Update existing status
        await statusService.updateStatusRecord(existingStatus.id, {
          entity_id: entity.id,
          project_id: project.id,
          status,
          notes,
          updated_by: 'admin', // Replace with actual user
        });
      } else {
        // Create new status
        await statusService.createStatusRecord({
          entity_id: entity.id,
          project_id: project.id,
          status,
          notes,
          updated_by: 'admin', // Replace with actual user
        });
      }

      if (onStatusUpdated) {
        onStatusUpdated();
      }
    } catch (err) {
      console.error('Error updating status:', err);
      setError('Failed to update status');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      sx={{
        p: 3,
        mb: 3,
        borderRadius: 2,
        boxShadow: '0 2px 10px rgba(0,0,0,0.08)',
        border: `1px solid ${getStatusColor(existingStatus?.status)}`,
        background: `linear-gradient(to right, ${getStatusBgColor(existingStatus?.status)}, transparent)`,
      }}
    >
      <Grid container spacing={3}>
        {/* Entity Header */}
        <Grid item xs={12}>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar
              sx={{
                bgcolor: getStatusColor(existingStatus?.status),
                width: 56,
                height: 56,
              }}
            >
              <PersonIcon />
            </Avatar>
            <Box>
              <Typography variant="h5" fontWeight="600">
                {entity.name}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                {entity.title} • {entity.district || entity.entity_type}
              </Typography>
            </Box>
            {!isAdmin && existingStatus && (
              <Chip
                label={getStatusLabel(existingStatus.status)}
                sx={{
                  ml: 'auto',
                  bgcolor: getStatusColor(existingStatus.status),
                  color: '#fff',
                  fontWeight: 500,
                  fontSize: '0.9rem',
                  padding: '20px 10px',
                }}
              />
            )}
          </Box>
        </Grid>

        {/* Contact Information */}
        <Grid item xs={12} md={6}>
          <Paper
            elevation={0}
            sx={{
              p: 2,
              bgcolor: 'rgba(0,0,0,0.02)',
              borderRadius: 1,
            }}
          >
            <Typography variant="subtitle2" gutterBottom>
              Contact Information
            </Typography>
            <Box display="flex" flexDirection="column" gap={1} mt={1}>
              {entity.email && (
                <Box display="flex" alignItems="center" gap={1}>
                  <EmailIcon fontSize="small" color="action" />
                  <Link href={`mailto:${entity.email}`}>{entity.email}</Link>
                </Box>
              )}

              {entity.phone && (
                <Box display="flex" alignItems="center" gap={1}>
                  <PhoneIcon fontSize="small" color="action" />
                  <Link href={`tel:${entity.phone}`}>{entity.phone}</Link>
                </Box>
              )}

              {entity.website && (
                <Box display="flex" alignItems="center" gap={1}>
                  <PublicIcon fontSize="small" color="action" />
                  <Link href={entity.website} target="_blank" rel="noopener">
                    Website
                  </Link>
                </Box>
              )}

              {entity.address && (
                <Box display="flex" alignItems="flex-start" gap={1}>
                  <LocationOnIcon fontSize="small" color="action" sx={{ mt: 0.3 }} />
                  <Typography variant="body2">{entity.address}</Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Status Controls */}
        <Grid item xs={12} md={6}>
          {isAdmin ? (
            <>
              <Typography variant="subtitle2" gutterBottom>
                Update Status
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel id="status-select-label">Status</InputLabel>
                <Select
                  labelId="status-select-label"
                  id="status-select"
                  value={status}
                  label="Status"
                  onChange={handleStatusChange}
                  disabled={loading}
                >
                  <MenuItem value={EntityStatus.SOLID_APPROVAL}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        width={12}
                        height={12}
                        borderRadius="50%"
                        bgcolor={getStatusColor(EntityStatus.SOLID_APPROVAL)}
                      />
                      Strong Support
                    </Box>
                  </MenuItem>
                  <MenuItem value={EntityStatus.LEANING_APPROVAL}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        width={12}
                        height={12}
                        borderRadius="50%"
                        bgcolor={getStatusColor(EntityStatus.LEANING_APPROVAL)}
                      />
                      Tentative Support
                    </Box>
                  </MenuItem>
                  <MenuItem value={EntityStatus.NEUTRAL}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        width={12}
                        height={12}
                        borderRadius="50%"
                        bgcolor={getStatusColor(EntityStatus.NEUTRAL)}
                      />
                      Undecided
                    </Box>
                  </MenuItem>
                  <MenuItem value={EntityStatus.LEANING_DISAPPROVAL}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        width={12}
                        height={12}
                        borderRadius="50%"
                        bgcolor={getStatusColor(EntityStatus.LEANING_DISAPPROVAL)}
                      />
                      Tentative Opposition
                    </Box>
                  </MenuItem>
                  <MenuItem value={EntityStatus.SOLID_DISAPPROVAL}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        width={12}
                        height={12}
                        borderRadius="50%"
                        bgcolor={getStatusColor(EntityStatus.SOLID_DISAPPROVAL)}
                      />
                      Strong Opposition
                    </Box>
                  </MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={notes}
                onChange={handleNotesChange}
                disabled={loading}
                sx={{ mb: 2 }}
              />

              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                disabled={loading}
                sx={{ minWidth: 120 }}
              >
                {loading ? 'Saving...' : existingStatus ? 'Update' : 'Save'}
              </Button>

              {error && (
                <Typography color="error" sx={{ mt: 1 }}>
                  {error}
                </Typography>
              )}
            </>
          ) : (
            existingStatus && (
              <>
                <Typography variant="subtitle2" gutterBottom>
                  Current Status
                </Typography>
                <Box
                  p={2}
                  bgcolor={getStatusBgColor(existingStatus.status)}
                  borderRadius={1}
                  border={`1px solid ${getStatusColor(existingStatus.status)}`}
                >
                  <Typography fontWeight="600" color={getStatusColor(existingStatus.status)}>
                    {getStatusLabel(existingStatus.status)}
                  </Typography>

                  {existingStatus.notes && (
                    <>
                      <Divider sx={{ my: 1.5 }} />
                      <Typography variant="body2">{existingStatus.notes}</Typography>
                    </>
                  )}

                  <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                    Last updated: {new Date(existingStatus.updated_at).toLocaleString()}
                  </Typography>
                </Box>
              </>
            )
          )}
        </Grid>
      </Grid>
    </Paper>
  );
};

export default EntityStatusManager;

import React, { useState } from 'react';
import {
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Paper,
  Grid,
  SelectChangeEvent,
  Chip,
} from '@mui/material';
import { EntityStatus, Entity, Project, EntityStatusRecord } from '../../types';
import { statusService } from '../../services/status';

interface EntityStatusManagerProps {
  entity: Entity;
  project: Project;
  existingStatus?: EntityStatusRecord;
  onStatusUpdated?: () => void;
  isAdmin?: boolean;
}

const getStatusColor = (
  status: EntityStatus
): 'success' | 'info' | 'warning' | 'error' | 'default' => {
  switch (status) {
    case EntityStatus.SOLID_APPROVAL:
      return 'success';
    case EntityStatus.LEANING_APPROVAL:
      return 'info';
    case EntityStatus.NEUTRAL:
      return 'default';
    case EntityStatus.LEANING_DISAPPROVAL:
      return 'warning';
    case EntityStatus.SOLID_DISAPPROVAL:
      return 'error';
    default:
      return 'default';
  }
};

const getStatusLabel = (status: EntityStatus): string => {
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
          status,
          notes,
          updated_by: 'admin', // TODO: Replace with actual user
        });
      } else {
        // Create new status
        await statusService.createStatusRecord({
          entity_id: entity.id,
          project_id: project.id,
          status,
          notes,
          updated_by: 'admin', // TODO: Replace with actual user
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
    <Paper sx={{ p: 3, mb: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Status for {entity.name}</Typography>
            {!isAdmin && existingStatus && (
              <Chip
                label={getStatusLabel(existingStatus.status)}
                color={getStatusColor(existingStatus.status)}
              />
            )}
          </Box>
        </Grid>

        {isAdmin ? (
          <>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
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
                    <Chip size="small" label="Solid Approval" color="success" sx={{ mr: 1 }} />
                    Strong Support
                  </MenuItem>
                  <MenuItem value={EntityStatus.LEANING_APPROVAL}>
                    <Chip size="small" label="Leaning Approval" color="info" sx={{ mr: 1 }} />
                    Tentative Support
                  </MenuItem>
                  <MenuItem value={EntityStatus.NEUTRAL}>
                    <Chip size="small" label="Neutral" color="default" sx={{ mr: 1 }} />
                    Undecided
                  </MenuItem>
                  <MenuItem value={EntityStatus.LEANING_DISAPPROVAL}>
                    <Chip size="small" label="Leaning Disapproval" color="warning" sx={{ mr: 1 }} />
                    Tentative Opposition
                  </MenuItem>
                  <MenuItem value={EntityStatus.SOLID_DISAPPROVAL}>
                    <Chip size="small" label="Solid Disapproval" color="error" sx={{ mr: 1 }} />
                    Strong Opposition
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={notes}
                onChange={handleNotesChange}
                disabled={loading}
              />
            </Grid>

            <Grid item xs={12}>
              <Button variant="contained" color="primary" onClick={handleSubmit} disabled={loading}>
                {loading ? 'Saving...' : existingStatus ? 'Update Status' : 'Save Status'}
              </Button>
              {error && (
                <Typography color="error" sx={{ mt: 1 }}>
                  {error}
                </Typography>
              )}
            </Grid>
          </>
        ) : (
          existingStatus?.notes && (
            <Grid item xs={12}>
              <Typography variant="subtitle2">Notes:</Typography>
              <Typography variant="body2" color="text.secondary">
                {existingStatus.notes}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                Last updated: {new Date(existingStatus.updated_at).toLocaleString()}
              </Typography>
            </Grid>
          )
        )}
      </Grid>
    </Paper>
  );
};

export default EntityStatusManager;

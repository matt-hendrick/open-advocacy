import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
  SelectChangeEvent,
  Paper,
  Grid,
} from '@mui/material';
import { ProjectStatus, EntityStatus, Project, Jurisdiction } from '../../types';
import { projectService } from '../../services/projects';
import { jurisdictionService } from '../../services/jurisdictions';

interface ProjectFormProps {
  project?: Project;
  onSubmit?: (project: Project) => void;
  onCancel?: () => void;
}

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

const ProjectForm: React.FC<ProjectFormProps> = ({ project, onSubmit, onCancel }) => {
  const [title, setTitle] = useState(project?.title || '');
  const [description, setDescription] = useState(project?.description || '');
  const [status, setStatus] = useState<ProjectStatus>(project?.status || ProjectStatus.DRAFT);
  const [link, setLink] = useState(project?.link || '');
  const [preferredStatus, setPreferredStatus] = useState<EntityStatus>(
    project?.preferred_status || EntityStatus.SOLID_APPROVAL
  );
  const [templateResponse, setTemplateResponse] = useState(project?.template_response || '');
  const [selectedJurisdictions, setSelectedJurisdictions] = useState<string[]>(
    project?.jurisdictions || []
  );

  const [jurisdictions, setJurisdictions] = useState<Jurisdiction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJurisdictions = async () => {
      try {
        const response = await jurisdictionService.getJurisdictions();
        setJurisdictions(response.data);
      } catch (err) {
        console.error('Error fetching jurisdictions:', err);
        setError('Failed to load jurisdictions');
      }
    };

    fetchJurisdictions();
  }, []);

  const handleJurisdictionChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    setSelectedJurisdictions(typeof value === 'string' ? [value] : value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const projectData = {
        title,
        description,
        status,
        active: true,
        link,
        preferred_status: preferredStatus,
        template_response: templateResponse,
        jurisdictions: selectedJurisdictions,
      };

      let response;
      if (project) {
        response = await projectService.updateProject(project.id, projectData);
      } else {
        response = await projectService.createProject(projectData);
      }

      if (onSubmit) {
        onSubmit(response.data);
      }
    } catch (err) {
      console.error('Error saving project:', err);
      setError('Failed to save project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" mb={3}>
        {project ? 'Edit Project' : 'Create New Project'}
      </Typography>

      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              label="Title"
              fullWidth
              required
              value={title}
              onChange={e => setTitle(e.target.value)}
              disabled={loading}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={description}
              onChange={e => setDescription(e.target.value)}
              disabled={loading}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={status}
                label="Status"
                onChange={e => setStatus(e.target.value as ProjectStatus)}
                disabled={loading}
              >
                <MenuItem value={ProjectStatus.DRAFT}>Draft</MenuItem>
                <MenuItem value={ProjectStatus.ACTIVE}>Active</MenuItem>
                <MenuItem value={ProjectStatus.COMPLETED}>Completed</MenuItem>
                <MenuItem value={ProjectStatus.ARCHIVED}>Archived</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label="Link"
              fullWidth
              value={link}
              onChange={e => setLink(e.target.value)}
              disabled={loading}
              placeholder="https://example.com"
            />
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Preferred Status</InputLabel>
              <Select
                value={preferredStatus}
                label="Preferred Status"
                onChange={e => setPreferredStatus(e.target.value as EntityStatus)}
                disabled={loading}
              >
                <MenuItem value={EntityStatus.SOLID_APPROVAL}>Solid Approval</MenuItem>
                <MenuItem value={EntityStatus.LEANING_APPROVAL}>Leaning Approval</MenuItem>
                <MenuItem value={EntityStatus.NEUTRAL}>Neutral</MenuItem>
                <MenuItem value={EntityStatus.LEANING_DISAPPROVAL}>Leaning Disapproval</MenuItem>
                <MenuItem value={EntityStatus.SOLID_DISAPPROVAL}>Solid Disapproval</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Jurisdictions</InputLabel>
              <Select
                multiple
                value={selectedJurisdictions}
                onChange={handleJurisdictionChange}
                input={<OutlinedInput label="Jurisdictions" />}
                renderValue={selected => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map(value => {
                      const jurisdiction = jurisdictions.find(j => j.id === value);
                      return (
                        <Chip
                          key={value}
                          label={jurisdiction ? jurisdiction.name : value}
                          size="small"
                        />
                      );
                    })}
                  </Box>
                )}
                MenuProps={MenuProps}
                disabled={loading}
              >
                {jurisdictions.map(jurisdiction => (
                  <MenuItem key={jurisdiction.id} value={jurisdiction.id}>
                    {jurisdiction.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="Template Response"
              fullWidth
              multiline
              rows={4}
              value={templateResponse}
              onChange={e => setTemplateResponse(e.target.value)}
              disabled={loading}
              placeholder="Template response for advocates to use"
            />
          </Grid>

          {error && (
            <Grid item xs={12}>
              <Typography color="error">{error}</Typography>
            </Grid>
          )}

          <Grid item xs={12}>
            <Box display="flex" justifyContent="flex-end" gap={2}>
              {onCancel && (
                <Button onClick={onCancel} disabled={loading}>
                  Cancel
                </Button>
              )}
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading || !title}
              >
                {loading ? 'Saving...' : project ? 'Update Project' : 'Create Project'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default ProjectForm;

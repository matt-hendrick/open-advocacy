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
  Paper,
  Grid,
  FormHelperText,
} from '@mui/material';
import { ProjectStatus, EntityStatus, Project, Jurisdiction } from '../../types';
import { projectService } from '../../services/projects';
import { jurisdictionService } from '../../services/jurisdictions';
import { groupService } from '../../services/groups';

interface ProjectFormProps {
  project?: Project;
  onSubmit?: (project: Project) => void;
  onCancel?: () => void;
}

const ProjectForm: React.FC<ProjectFormProps> = ({ project, onSubmit, onCancel }) => {
  const [title, setTitle] = useState(project?.title || '');
  const [description, setDescription] = useState(project?.description || '');
  const [status, setStatus] = useState<ProjectStatus>(project?.status || ProjectStatus.DRAFT);
  const [link, setLink] = useState(project?.link || '');
  const [preferredStatus, setPreferredStatus] = useState<EntityStatus>(
    project?.preferred_status || EntityStatus.SOLID_APPROVAL
  );
  const [templateResponse, setTemplateResponse] = useState(project?.template_response || '');
  const [jurisdictionId, setJurisdictionId] = useState<string>(project?.jurisdiction_id || '');
  const [groupId, setGroupId] = useState<string>(project?.group_id || '');

  const [titleError, setTitleError] = useState('');
  const [jurisdictionError, setJurisdictionError] = useState('');

  const [jurisdictions, setJurisdictions] = useState<Jurisdiction[]>([]);
  const [groups, setGroups] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [jurisdictionsResponse, groupsResponse] = await Promise.all([
          jurisdictionService.getJurisdictions(),
          groupService.getGroups(),
        ]);
        setJurisdictions(jurisdictionsResponse.data);
        setGroups(groupsResponse.data);
      } catch (err) {
        console.error('Error fetching form data:', err);
        setError('Failed to load form data');
      }
    };

    fetchData();
  }, []);

  const validateForm = () => {
    let isValid = true;

    // Validate title
    if (!title.trim()) {
      setTitleError('Title is required');
      isValid = false;
    } else {
      setTitleError('');
    }

    // Validate jurisdiction
    if (!jurisdictionId) {
      setJurisdictionError('Jurisdiction is required');
      isValid = false;
    } else {
      setJurisdictionError('');
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

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
        jurisdiction_id: jurisdictionId,
        group_id: groupId || undefined,
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
              error={!!titleError}
              helperText={titleError}
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
            <FormControl fullWidth error={!!jurisdictionError}>
              <InputLabel>Jurisdiction</InputLabel>
              <Select
                value={jurisdictionId}
                label="Jurisdiction"
                onChange={e => setJurisdictionId(e.target.value)}
                disabled={loading}
                required
              >
                {jurisdictions.map(jurisdiction => (
                  <MenuItem key={jurisdiction.id} value={jurisdiction.id}>
                    {jurisdiction.name}
                  </MenuItem>
                ))}
              </Select>
              {jurisdictionError && <FormHelperText>{jurisdictionError}</FormHelperText>}
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Group</InputLabel>
              <Select
                value={groupId}
                label="Group"
                onChange={e => setGroupId(e.target.value)}
                disabled={loading}
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {groups.map(group => (
                  <MenuItem key={group.id} value={group.id}>
                    {group.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
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

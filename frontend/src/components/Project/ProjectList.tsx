import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  Box,
  Divider,
  useTheme,
  Paper,
  InputBase,
  IconButton,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  CircularProgress,
  SelectChangeEvent,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import { projectService } from '../../services/projects';
import { Project, ProjectStatus } from '../../types';
import ErrorDisplay from '../common/ErrorDisplay';
import { transformProjectFromApi } from '../../utils/dataTransformers';
import StatusDistribution from '../Status/StatusDistribution';

const getStatusColor = (status: ProjectStatus): 'success' | 'default' | 'info' | 'secondary' => {
  switch (status) {
    case ProjectStatus.ACTIVE:
      return 'success';
    case ProjectStatus.DRAFT:
      return 'default';
    case ProjectStatus.COMPLETED:
      return 'info';
    case ProjectStatus.ARCHIVED:
      return 'secondary';
    default:
      return 'default';
  }
};

const getStatusLabel = (status: ProjectStatus): string => {
  return status.charAt(0).toUpperCase() + status.slice(1);
};

const ProjectList: React.FC = () => {
  const theme = useTheme();
  const [projects, setProjects] = useState<Project[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const navigate = useNavigate();

  const fetchProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await projectService.getProjects();
      // Transform data if needed
      const transformedProjects = response.data.map(transformProjectFromApi);
      setProjects(transformedProjects);
      setFilteredProjects(transformedProjects);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to load projects. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    const filtered = projects.filter(project => {
      const matchesSearch =
        project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        false;
      const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
    setFilteredProjects(filtered);
  }, [searchTerm, statusFilter, projects]);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleStatusFilterChange = (event: SelectChangeEvent) => {
    setStatusFilter(event.target.value);
  };

  if (loading)
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" py={8}>
          <CircularProgress />
        </Box>
      </Container>
    );

  if (error)
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <ErrorDisplay message={error} onRetry={fetchProjects} />
      </Container>
    );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box mb={4}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h4" component="h1" fontWeight="700" color="text.primary">
            Advocacy Projects
          </Typography>

          <Button variant="contained" color="primary" onClick={() => navigate('/projects/create')}>
            Create Project
          </Button>
        </Box>
        <Typography variant="body1" color="text.secondary" mb={4}>
          Browse projects, check their status, and find ways to support causes you care about.
        </Typography>

        <Box
          display="flex"
          flexDirection={{ xs: 'column', md: 'row' }}
          gap={2}
          alignItems={{ xs: 'stretch', md: 'center' }}
          sx={{ mb: 4 }}
        >
          <Paper
            sx={{
              p: '2px 4px',
              display: 'flex',
              alignItems: 'center',
              flexGrow: 1,
              boxShadow: '0px 2px 8px rgba(0,0,0,0.05)',
              borderRadius: theme.shape.borderRadius,
            }}
          >
            <IconButton sx={{ p: '10px' }} aria-label="search">
              <SearchIcon />
            </IconButton>
            <InputBase
              sx={{ ml: 1, flex: 1 }}
              placeholder="Search projects"
              inputProps={{ 'aria-label': 'search projects' }}
              value={searchTerm}
              onChange={handleSearchChange}
            />
          </Paper>

          <FormControl variant="outlined" sx={{ minWidth: 180 }}>
            <InputLabel id="status-filter-label">Filter by Status</InputLabel>
            <Select
              labelId="status-filter-label"
              id="status-filter"
              value={statusFilter}
              onChange={handleStatusFilterChange}
              label="Filter by Status"
              startAdornment={<FilterListIcon sx={{ mr: 1, ml: -0.5 }} />}
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value={ProjectStatus.ACTIVE}>Active</MenuItem>
              <MenuItem value={ProjectStatus.DRAFT}>Draft</MenuItem>
              <MenuItem value={ProjectStatus.COMPLETED}>Completed</MenuItem>
              <MenuItem value={ProjectStatus.ARCHIVED}>Archived</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {filteredProjects.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center', borderRadius: theme.shape.borderRadius }}>
          <Typography variant="h6" color="text.secondary">
            No projects found matching your criteria
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={1}>
            Try adjusting your search or filter settings
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredProjects.map(project => (
            <Grid item xs={12} md={6} lg={4} key={project.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 20px -10px rgba(0,0,0,0.1)',
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography
                      variant="h6"
                      component="h2"
                      fontWeight="600"
                      color="text.primary"
                      sx={{
                        cursor: 'pointer',
                        '&:hover': {
                          color: theme.palette.primary.main,
                          textDecoration: 'underline',
                        },
                      }}
                      onClick={() => navigate(`/projects/${project.id}`)}
                    >
                      {project.title}
                    </Typography>
                    <Chip
                      label={getStatusLabel(project.status)}
                      color={getStatusColor(project.status)}
                      size="small"
                      sx={{ fontWeight: 500 }}
                    />
                  </Box>

                  {project.status_distribution && (
                    <Box mt={2} mb={2}>
                      <StatusDistribution
                        distribution={project.status_distribution}
                        size="small"
                        showLabels={true}
                      />
                    </Box>
                  )}

                  <Typography variant="body2" color="text.secondary" paragraph sx={{ mb: 3 }}>
                    {project.description}
                  </Typography>

                  <Divider sx={{ mb: 2 }} />

                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box display="flex" alignItems="center">
                      <AccessTimeIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
                      <Typography variant="caption" color="text.secondary">
                        Updated: {new Date(project.updated_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
                <CardActions sx={{ px: 2, pb: 2 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    color="primary"
                    sx={{ mr: 1, borderRadius: theme.shape.borderRadius }}
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    View Details
                  </Button>
                  <Button
                    size="small"
                    variant="contained"
                    color="primary"
                    sx={{ borderRadius: theme.shape.borderRadius }}
                  >
                    Contact Reps
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default ProjectList;

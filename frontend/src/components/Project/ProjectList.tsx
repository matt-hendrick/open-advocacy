import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Card, CardContent, 
  CardActions, Button, Grid, Chip, Box 
} from '@mui/material';
import { projectService } from '../../services/projects';
import { Project, ProjectStatus } from '../../types';

const getStatusColor = (status: ProjectStatus): "success" | "default" | "info" | "secondary" => {
  switch (status) {
    case ProjectStatus.ACTIVE: return 'success';
    case ProjectStatus.DRAFT: return 'default';
    case ProjectStatus.COMPLETED: return 'info';
    case ProjectStatus.ARCHIVED: return 'secondary';
    default: return 'default';
  }
};

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await projectService.getProjects();
        setProjects(response.data);
        setLoading(false);
      } catch (err) {
        setError('Error loading projects');
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  if (loading) return <Typography>Loading projects...</Typography>;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Advocacy Projects
      </Typography>
      
      <Grid container spacing={3}>
        {projects.map((project) => (
          <Grid item xs={12} md={6} lg={4} key={project.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6" component="h2">
                    {project.title}
                  </Typography>
                  <Chip 
                    label={project.status} 
                    color={getStatusColor(project.status)} 
                    size="small" 
                  />
                </Box>
                
                <Typography variant="body2" color="textSecondary" paragraph>
                  {project.description}
                </Typography>
                
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" color="textSecondary">
                    Votes: {project.vote_count}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Updated: {new Date(project.updated_at).toLocaleDateString()}
                  </Typography>
                </Box>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary">
                  View Details
                </Button>
                <Button size="small">
                  Contact Representatives
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default ProjectList;
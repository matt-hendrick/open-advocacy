import React from 'react';
import { Container, Typography, Box, Button } from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ProjectForm from '../components/Project/ProjectForm';
import { Project } from '../types';

const ProjectFormPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const handleSubmit = async (project: Project) => {
    // Navigate to the project details page after submission
    navigate(`/projects/${project.id}`);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box mb={4}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/projects')} sx={{ mb: 2 }}>
          Back to Projects
        </Button>

        <Typography variant="h4" component="h1" fontWeight="700" color="text.primary" gutterBottom>
          {isEditing ? 'Edit Project' : 'Create New Project'}
        </Typography>
      </Box>

      <ProjectForm
        project={undefined} // TODO: When editing, fetch and pass the project here
        onSubmit={handleSubmit}
        onCancel={() => navigate('/projects')}
      />
    </Container>
  );
};

export default ProjectFormPage;

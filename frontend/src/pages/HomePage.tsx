import React from 'react';
import { Container, Typography, Paper, Button, Box, Grid } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { appConfig } from '@/utils/config';

const HomePage: React.FC = () => {
  return (
    <Container>
      <Box py={8} textAlign="center">
        <Typography variant="h3" component="h1" gutterBottom>
          {appConfig.name}
        </Typography>

        <Typography variant="h5" color="textSecondary" paragraph>
          {appConfig.description}
        </Typography>

        <Grid container spacing={4} justifyContent="center" mt={4}>
          <Grid size={{ xs: 12, md: 4 }}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h5" gutterBottom>
                Find Your Representatives
              </Typography>
              <Typography paragraph>
                Enter your address to find the elected officials who represent you and learn how to
                contact them.
              </Typography>
              <Button
                variant="contained"
                color="primary"
                component={RouterLink}
                to="/representatives"
              >
                Get Started
              </Button>
            </Paper>
          </Grid>

          <Grid size={{ xs: 12, md: 4 }}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h5" gutterBottom>
                Explore Projects
              </Typography>
              <Typography paragraph>
                Browse ongoing advocacy projects, see their status, and find ways to support causes
                you care about.
              </Typography>
              <Button variant="contained" color="primary" component={RouterLink} to="/projects">
                View Projects
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default HomePage;

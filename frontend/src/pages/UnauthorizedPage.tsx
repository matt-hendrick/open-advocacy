import React from 'react';
import { Container, Typography, Box, Button, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import BlockIcon from '@mui/icons-material/Block';

const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          mt: 8,
          mb: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            borderRadius: 2,
          }}
        >
          <BlockIcon color="error" sx={{ fontSize: 64, mb: 2 }} />

          <Typography component="h1" variant="h4" gutterBottom align="center">
            Access Denied
          </Typography>

          <Typography variant="body1" align="center" sx={{ mb: 4 }}>
            Sorry, you don't have permission to access this page. Please contact your administrator
            if you believe this is an error.
          </Typography>

          <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
            <Button variant="contained" color="primary" onClick={() => navigate('/')}>
              Go to Home
            </Button>

            <Button variant="outlined" onClick={() => navigate(-1)}>
              Go Back
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default UnauthorizedPage;

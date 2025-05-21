import React from 'react';
import { Container, Box, Typography } from '@mui/material';

interface AdminLayoutProps {
  children: React.ReactNode;
  title?: string;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children, title = 'User Management' }) => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {title}
        </Typography>

        {children}
      </Box>
    </Container>
  );
};

export default AdminLayout;

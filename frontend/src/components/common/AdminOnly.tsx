import React, { ReactNode } from 'react';
import { Typography, Box, Button } from '@mui/material';

interface AdminOnlyProps {
  children: ReactNode;
  isAdmin?: boolean;
  fallbackMessage?: string;
}

// TODO: Replace Placeholder fake auth system
const AdminOnly: React.FC<AdminOnlyProps> = ({
  children,
  isAdmin = false,
  fallbackMessage = 'You need administrator access to view this content.',
}) => {
  return isAdmin ? (
    <>{children}</>
  ) : (
    <Box
      sx={{
        p: 4,
        textAlign: 'center',
        bgcolor: 'background.paper',
        borderRadius: 1,
      }}
    >
      <Typography variant="h6" gutterBottom>
        Access Restricted
      </Typography>
      <Typography variant="body1" paragraph>
        {fallbackMessage}
      </Typography>
      <Button variant="contained" color="primary" onClick={() => (window.location.href = '/')}>
        Return to Home
      </Button>
    </Box>
  );
};

export default AdminOnly;

import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Open Advocacy
        </Typography>
        <Box>
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/"
          >
            Home
          </Button>
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/projects"
          >
            Projects
          </Button>
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/representatives"
          >
            Find Representatives
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
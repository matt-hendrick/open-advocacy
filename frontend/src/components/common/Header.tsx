// src/components/common/Header.tsx
import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  useTheme,
  IconButton,
} from '@mui/material';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import VolunteerActivismIcon from '@mui/icons-material/VolunteerActivism';
import { useTheme as useCustomTheme } from '../../theme/ThemeProvider';
import { lightTheme, darkTheme } from '../../theme/themes';

const Header: React.FC = () => {
  const theme = useTheme();
  const { currentTheme, setTheme } = useCustomTheme();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const toggleTheme = () => {
    setTheme(currentTheme.name === 'light' ? darkTheme : lightTheme);
  };

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        backgroundColor: theme.palette.background.paper,
        borderBottom: `1px solid ${theme.palette.divider}`,
      }}
    >
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ height: 64 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <VolunteerActivismIcon
              sx={{
                mr: 1.5,
                color: theme.palette.primary.main,
                fontSize: 28,
              }}
            />
            <Typography
              variant="h6"
              component={RouterLink}
              to="/"
              sx={{
                color: theme.palette.text.primary,
                textDecoration: 'none',
                fontWeight: 700,
                letterSpacing: '0.5px',
              }}
            >
              Open Advocacy
            </Typography>
          </Box>

          <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center' }}>
            <Button
              color="inherit"
              component={RouterLink}
              to="/"
              sx={{
                mx: 1,
                color: isActive('/') ? theme.palette.primary.main : theme.palette.text.primary,
                fontWeight: isActive('/') ? 700 : 500,
                '&:hover': {
                  backgroundColor: 'rgba(25, 118, 210, 0.04)',
                },
              }}
            >
              Home
            </Button>
            <Button
              color="inherit"
              component={RouterLink}
              to="/projects"
              sx={{
                mx: 1,
                color: isActive('/projects')
                  ? theme.palette.primary.main
                  : theme.palette.text.primary,
                fontWeight: isActive('/projects') ? 700 : 500,
                '&:hover': {
                  backgroundColor: 'rgba(25, 118, 210, 0.04)',
                },
              }}
            >
              Projects
            </Button>
            <Button
              color="inherit"
              component={RouterLink}
              to="/representatives"
              sx={{
                mx: 1,
                color: isActive('/representatives')
                  ? theme.palette.primary.main
                  : theme.palette.text.primary,
                fontWeight: isActive('/representatives') ? 700 : 500,
                '&:hover': {
                  backgroundColor: 'rgba(25, 118, 210, 0.04)',
                },
              }}
            >
              Find Representatives
            </Button>
          </Box>

          <Box>
            <IconButton
              onClick={toggleTheme}
              color="inherit"
              sx={{ color: theme.palette.text.primary }}
            >
              {currentTheme.name === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;

import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  useTheme,
  IconButton,
  Tooltip,
  Popover,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
  Paper,
  ButtonBase,
} from '@mui/material';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import VolunteerActivismIcon from '@mui/icons-material/VolunteerActivism';
import PersonIcon from '@mui/icons-material/Person';
import PlaceIcon from '@mui/icons-material/Place';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { useTheme as useCustomTheme } from '../../theme/ThemeProvider';
import { lightTheme, darkTheme } from '../../theme/themes';
import { useUserRepresentatives } from '../../contexts/UserRepresentativesContext';

const Header: React.FC = () => {
  const theme = useTheme();
  const { currentTheme, setTheme } = useCustomTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const { hasUserRepresentatives, userRepresentatives, userAddress } = useUserRepresentatives();

  // State for representative popover
  const [repAnchorEl, setRepAnchorEl] = useState<HTMLElement | null>(null);

  const handleRepClick = (event: React.MouseEvent<HTMLElement>) => {
    setRepAnchorEl(event.currentTarget);
  };

  const handleRepClose = () => {
    setRepAnchorEl(null);
  };

  const repPopoverOpen = Boolean(repAnchorEl);

  const handleEntityClick = (entityId: string) => {
    navigate(`/representatives/${entityId}`);
    handleRepClose();
  };

  const isActive = (path: string) => location.pathname === path;

  const toggleTheme = () => {
    setTheme(currentTheme.name === 'light' ? darkTheme : lightTheme);
  };

  // Representative badge and popover
  const RepresentativeBadge = () => {
    if (!hasUserRepresentatives) return null;

    return (
      <>
        <Tooltip title={`Your representatives for: ${userAddress}`}>
          <Chip
            icon={<PersonIcon />}
            label={`${userRepresentatives.length} Saved Representative${userRepresentatives.length > 1 ? 's' : ''}`}
            color="primary"
            variant="outlined"
            onClick={handleRepClick}
            sx={{
              ml: 2,
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: theme.palette.primary.main + '1A', // 10% opacity
              },
            }}
          />
        </Tooltip>

        <Popover
          open={repPopoverOpen}
          anchorEl={repAnchorEl}
          onClose={handleRepClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'center',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'center',
          }}
        >
          <Paper sx={{ width: 320, maxHeight: 400, overflow: 'auto' }}>
            <Box sx={{ p: 2, borderBottom: `1px solid ${theme.palette.divider}` }}>
              <Typography variant="subtitle1" fontWeight="bold">
                Your Representatives
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Based on: {userAddress}
              </Typography>
            </Box>

            <List dense>
              {userRepresentatives.map(rep => (
                <ListItem
                  key={rep.id}
                  component={ButtonBase}
                  onClick={() => handleEntityClick(rep.id)}
                  sx={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '8px 16px',
                    '&:hover': {
                      backgroundColor: theme.palette.action.hover,
                    },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <PersonIcon color="primary" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body2" component="span">
                        <strong>{rep.name}</strong>
                      </Typography>
                    }
                    secondary={
                      <Typography component="span" variant="caption">
                        <Box
                          component="span"
                          sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                        >
                          <PlaceIcon sx={{ fontSize: 14 }} />
                          <span>{rep.district_name || rep.title || 'Representative'}</span>
                        </Box>
                      </Typography>
                    }
                  />
                  <ArrowForwardIcon fontSize="small" color="action" sx={{ opacity: 0.6 }} />
                </ListItem>
              ))}
            </List>

            <Divider />

            <Box sx={{ p: 1.5, textAlign: 'center' }}>
              <Button
                size="small"
                variant="outlined"
                component={RouterLink}
                to="/representatives"
                onClick={handleRepClose}
              >
                View All Representatives
              </Button>
            </Box>
          </Paper>
        </Popover>
      </>
    );
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

            {/* Representative badge with popover */}
            <RepresentativeBadge />
          </Box>

          <Box
            sx={{
              flexGrow: 1,
              display: 'flex',
              justifyContent: 'center',
              ml: 0,
            }}
          >
            <>
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
            </>
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

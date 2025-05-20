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
  Avatar,
  Menu,
  MenuItem,
} from '@mui/material';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import VolunteerActivismIcon from '@mui/icons-material/VolunteerActivism';
import PersonIcon from '@mui/icons-material/Person';
import PlaceIcon from '@mui/icons-material/Place';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import LoginIcon from '@mui/icons-material/Login';
import LogoutIcon from '@mui/icons-material/Logout';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import SupervisorAccountIcon from '@mui/icons-material/SupervisorAccount';
import { useTheme as useCustomTheme } from '../../theme/ThemeProvider';
import { lightTheme, darkTheme } from '../../theme/themes';
import { useUserRepresentatives } from '../../contexts/UserRepresentativesContext';
import { useAuth } from '../../contexts/AuthContext';
import ConditionalUI from '../auth/ConditionalUI';

const Header: React.FC = () => {
  const theme = useTheme();
  const { currentTheme, setTheme } = useCustomTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const { hasUserRepresentatives, userRepresentatives, userAddress } = useUserRepresentatives();
  const { user, logout, isAuthenticated, hasAnyRole } = useAuth();

  // State for representative popover
  const [repAnchorEl, setRepAnchorEl] = useState<HTMLElement | null>(null);
  // State for user menu
  const [userMenuAnchorEl, setUserMenuAnchorEl] = useState<null | HTMLElement>(null);

  const handleRepClick = (event: React.MouseEvent<HTMLElement>) => {
    setRepAnchorEl(event.currentTarget);
  };

  const handleRepClose = () => {
    setRepAnchorEl(null);
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleUserMenuClose();
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const handleEntityClick = (entityId: string) => {
    navigate(`/representatives/${entityId}`);
    handleRepClose();
  };

  const isActive = (path: string) => location.pathname === path;

  const toggleTheme = () => {
    setTheme(currentTheme.name === 'light' ? darkTheme : lightTheme);
  };

  const repPopoverOpen = Boolean(repAnchorEl);
  const userMenuOpen = Boolean(userMenuAnchorEl);

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
                    {rep.image_url ? (
                      <Avatar
                        src={rep.image_url}
                        sx={{
                          width: 24,
                          height: 24,
                        }}
                      >
                        <PersonIcon fontSize="small" />
                      </Avatar>
                    ) : (
                      <PersonIcon color="primary" fontSize="small" />
                    )}
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
        <Toolbar
          disableGutters
          sx={{
            height: { xs: 56, sm: 64 },
            flexDirection: { xs: 'column', sm: 'row' },
          }}
        >
          <Box
            sx={{
              display: 'flex',
              width: { xs: '100%', sm: 'auto' },
              justifyContent: { xs: 'space-between', sm: 'flex-start' },
              alignItems: 'center',
            }}
          >
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

            {/* Representative badge with popover - only show if screen is large enough */}
            <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
              <RepresentativeBadge />
            </Box>
          </Box>

          <Box
            sx={{
              flexGrow: 1,
              display: { xs: 'none', sm: 'flex' }, // Hide on mobile
              justifyContent: 'center',
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

              {/* Admin link - only visible to admins */}
              <ConditionalUI requiredRoles={['super_admin', 'group_admin']}>
                <Button
                  color="inherit"
                  component={RouterLink}
                  to="/admin"
                  sx={{
                    mx: 1,
                    color: isActive('/admin')
                      ? theme.palette.primary.main
                      : theme.palette.text.primary,
                    fontWeight: isActive('/admin') ? 700 : 500,
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.04)',
                    },
                  }}
                >
                  Admin
                </Button>
              </ConditionalUI>
            </>
          </Box>

          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <IconButton
              onClick={toggleTheme}
              color="inherit"
              sx={{
                color: theme.palette.text.primary,
                mr: 1,
              }}
              aria-label={
                currentTheme.name === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
              }
            >
              {currentTheme.name === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>

            {/* Auth section - conditionally show login button or user menu */}
            {isAuthenticated ? (
              <>
                <Tooltip title="Account settings">
                  <IconButton
                    onClick={handleUserMenuOpen}
                    size="small"
                    aria-controls={userMenuOpen ? 'account-menu' : undefined}
                    aria-haspopup="true"
                    aria-expanded={userMenuOpen ? 'true' : undefined}
                    sx={{
                      ml: 1,
                      border: `1px solid ${theme.palette.divider}`,
                      borderRadius: 2,
                      padding: '4px 8px',
                      '&:hover': {
                        backgroundColor: theme.palette.action.hover,
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <AccountCircleIcon sx={{ mr: 1 }} />
                      <Typography
                        variant="body2"
                        sx={{ mr: 1, display: { xs: 'none', sm: 'block' } }}
                      >
                        {user?.full_name || user?.email || 'User'}
                      </Typography>
                    </Box>
                  </IconButton>
                </Tooltip>

                <Menu
                  anchorEl={userMenuAnchorEl}
                  id="account-menu"
                  open={userMenuOpen}
                  onClose={handleUserMenuClose}
                  transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                  anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                  PaperProps={{
                    elevation: 3,
                    sx: {
                      minWidth: 200,
                      mt: 1,
                      '& .MuiMenuItem-root': {
                        px: 2,
                        py: 1,
                      },
                    },
                  }}
                >
                  <MenuItem onClick={handleUserMenuClose} disabled>
                    <ListItemIcon>
                      <AccountCircleIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={user?.full_name || 'User'}
                      secondary={user?.email}
                      primaryTypographyProps={{ variant: 'body2' }}
                      secondaryTypographyProps={{ variant: 'caption' }}
                    />
                  </MenuItem>

                  <Divider />

                  {/* Admin menu item - only visible to admins */}
                  {hasAnyRole(['super_admin', 'group_admin']) && (
                    <MenuItem component={RouterLink} to="/admin" onClick={handleUserMenuClose}>
                      <ListItemIcon>
                        <AdminPanelSettingsIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary="Admin Panel" />
                    </MenuItem>
                  )}

                  {/* User management - only for admins */}
                  {hasAnyRole(['super_admin', 'group_admin']) && (
                    <MenuItem component={RouterLink} to="/register" onClick={handleUserMenuClose}>
                      <ListItemIcon>
                        <SupervisorAccountIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary="Add User" />
                    </MenuItem>
                  )}

                  {/* Logout option */}
                  <MenuItem onClick={handleLogout}>
                    <ListItemIcon>
                      <LogoutIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Logout" />
                  </MenuItem>
                </Menu>
              </>
            ) : (
              <Button
                variant="outlined"
                size="small"
                startIcon={<LoginIcon />}
                onClick={handleLogin}
                sx={{ ml: 1 }}
              >
                Sign In
              </Button>
            )}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;

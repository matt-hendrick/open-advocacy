import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Link,
  Divider,
  Box,
  CircularProgress,
  Alert,
  Paper,
  Chip,
  Snackbar,
  useTheme,
  Fade,
  IconButton,
  Tooltip,
} from '@mui/material';
import MuiAlert from '@mui/material/Alert';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import PublicIcon from '@mui/icons-material/Public';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import SearchIcon from '@mui/icons-material/Search';
import InfoIcon from '@mui/icons-material/Info';
import { Entity } from '../types';
import { entityService } from '../services/entities';
import { useNavigate } from 'react-router-dom';
import { useUserRepresentatives } from '../contexts/UserRepresentativesContext';

// RepresentativeBadge component for the header
export const RepresentativeBadge: React.FC = () => {
  const { hasUserRepresentatives, userRepresentatives, userAddress } = useUserRepresentatives();
  const navigate = useNavigate();
  const theme = useTheme();

  if (!hasUserRepresentatives) return null;

  return (
    <Tooltip title={`Your representatives based on: ${userAddress}`} placement="bottom">
      <Chip
        icon={<PersonIcon />}
        label={`${userRepresentatives.length} Representatives`}
        color="primary"
        variant="outlined"
        onClick={() => navigate('/representatives')}
        sx={{
          ml: 2,
          cursor: 'pointer',
          borderColor: theme.palette.primary.main,
          '&:hover': {
            backgroundColor: theme.palette.primary.main + '1A', // 10% opacity
          },
        }}
      />
    </Tooltip>
  );
};

// ProjectRepresentativeSection component for project details page
export const ProjectRepresentativeSection: React.FC<{ projectId: string }> = ({ projectId }) => {
  const { userRepresentatives, hasUserRepresentatives } = useUserRepresentatives();
  const [loading, setLoading] = useState<boolean>(true);
  const [repStatuses, setRepStatuses] = useState<{
    [key: string]: { status: string; notes: string | null };
  }>({});
  const theme = useTheme();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRepresentativeStatuses = async () => {
      if (!hasUserRepresentatives || !projectId) {
        setLoading(false);
        return;
      }

      try {
        // Fetch statuses for the user's representatives on this project
        const repIds = userRepresentatives.map(rep => rep.id);
        const response = await fetch(
          `/api/projects/${projectId}/entity-statuses?entity_ids=${repIds.join(',')}`
        );
        const data = await response.json();

        // Transform to object with rep ID as key
        const statusMap = {};
        data.forEach(status => {
          statusMap[status.entity_id] = {
            status: status.status,
            notes: status.notes,
          };
        });

        setRepStatuses(statusMap);
      } catch (error) {
        console.error('Error fetching representative statuses:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRepresentativeStatuses();
  }, [projectId, userRepresentatives, hasUserRepresentatives]);

  if (!hasUserRepresentatives) {
    return (
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          Your Representatives
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Find your representatives to see where they stand on this project.
        </Typography>
        <Button
          variant="outlined"
          color="primary"
          size="small"
          onClick={() => navigate('/representatives')}
          sx={{ mt: 2 }}
        >
          Find Representatives
        </Button>
      </Paper>
    );
  }

  if (loading) {
    return (
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress size={24} />
      </Paper>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'solid_approval':
        return theme.palette.success.main;
      case 'leaning_approval':
        return theme.palette.success.light;
      case 'neutral':
        return theme.palette.warning.main;
      case 'leaning_disapproval':
        return theme.palette.error.light;
      case 'solid_disapproval':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[400];
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'solid_approval':
        return 'Solid Approval';
      case 'leaning_approval':
        return 'Leaning Approval';
      case 'neutral':
        return 'Neutral';
      case 'leaning_disapproval':
        return 'Leaning Disapproval';
      case 'solid_disapproval':
        return 'Solid Disapproval';
      default:
        return 'Unknown';
    }
  };

  return (
    <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Where Your Representatives Stand
      </Typography>

      <List>
        {userRepresentatives.map(rep => {
          const status = repStatuses[rep.id]?.status || 'unknown';
          const notes = repStatuses[rep.id]?.notes;

          return (
            <ListItem
              key={rep.id}
              sx={{
                borderLeft: `4px solid ${getStatusColor(status)}`,
                mb: 1,
                backgroundColor: theme.palette.background.default,
                borderRadius: '0 4px 4px 0',
              }}
            >
              <ListItemAvatar>
                <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
                  <PersonIcon />
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="subtitle1">{rep.name}</Typography>
                    <Chip
                      label={getStatusLabel(status)}
                      size="small"
                      sx={{
                        ml: 1,
                        backgroundColor: getStatusColor(status),
                        color: '#fff',
                      }}
                    />
                  </Box>
                }
                secondary={
                  <>
                    <Typography variant="body2" color="textSecondary">
                      {rep.title} {rep.district_name ? `(${rep.district_name})` : ''}
                    </Typography>
                    {notes && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {notes}
                      </Typography>
                    )}
                  </>
                }
              />
              <Button
                variant="text"
                color="primary"
                onClick={() => navigate(`/contact?project=${projectId}&representative=${rep.id}`)}
              >
                Contact
              </Button>
            </ListItem>
          );
        })}
      </List>

      <Button
        variant="outlined"
        fullWidth
        onClick={() => navigate(`/contact?project=${projectId}`)}
        sx={{ mt: 2 }}
      >
        Contact All Your Representatives
      </Button>
    </Paper>
  );
};

const RepresentativeLookup: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();

  const { userRepresentatives, userAddress, updateUserRepresentatives, clearUserRepresentatives } =
    useUserRepresentatives();

  const [address, setAddress] = useState<string>(userAddress || '');
  const [representatives, setRepresentatives] = useState<Entity[]>(userRepresentatives || []);
  const [districts, setDistricts] = useState<string[]>([]);
  const [searched, setSearched] = useState<boolean>(userRepresentatives.length > 0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showToast, setShowToast] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string>('');

  const handleAddressChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setAddress(event.target.value);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!address.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await entityService.findByAddress(address);

      const reps = response.data.representatives || response.data;
      const foundDistricts = response.data.districts || [];

      setRepresentatives(reps);
      setDistricts(foundDistricts);
      setSearched(true);

      // Automatically save as user's representatives
      updateUserRepresentatives(reps, address, foundDistricts);

      // Show success toast
      setToastMessage(`Found ${reps.length} representatives for your address`);
      setShowToast(true);
    } catch (err) {
      setError('Failed to find representatives. Please try again.');
      console.error('Error fetching representatives:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearSearch = () => {
    setSearched(false);
    setRepresentatives([]);
    setAddress('');
    clearUserRepresentatives();
  };

  const handleViewProjects = (rep: Entity) => {
    navigate(`/projects?representative=${rep.id}`);
  };

  const handleCloseToast = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setShowToast(false);
  };

  const renderRepresentativeCards = (reps: Entity[]) => {
    if (reps.length === 0) {
      return (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1">No representatives found.</Typography>
        </Box>
      );
    }

    return (
      <Grid container spacing={3}>
        {reps.map(rep => (
          <Grid item xs={12} md={6} key={rep.id}>
            <Card
              elevation={3}
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6,
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Box display="flex" alignItems="center">
                    <Avatar sx={{ mr: 2, bgcolor: theme.palette.primary.main }}>
                      <PersonIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
                        {rep.name}
                      </Typography>
                      <Typography variant="subtitle2" color="textSecondary">
                        {rep.title}
                      </Typography>
                      {rep.district_name && (
                        <Chip
                          size="small"
                          label={rep.district_name}
                          color="primary"
                          variant="outlined"
                          sx={{ mt: 0.5 }}
                        />
                      )}
                    </Box>
                  </Box>
                </Box>

                <Divider sx={{ mb: 2 }} />

                <List dense>
                  {rep.email && (
                    <ListItem disablePadding sx={{ mb: 1 }}>
                      <ListItemAvatar>
                        <Avatar
                          sx={{ width: 28, height: 28, bgcolor: theme.palette.primary.light }}
                        >
                          <EmailIcon fontSize="small" />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="body2" color="textSecondary">
                            Email
                          </Typography>
                        }
                        secondary={
                          <Link
                            href={`mailto:${rep.email}`}
                            sx={{
                              display: 'inline-block',
                              maxWidth: '100%',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {rep.email}
                          </Link>
                        }
                      />
                    </ListItem>
                  )}

                  {rep.phone && (
                    <ListItem disablePadding sx={{ mb: 1 }}>
                      <ListItemAvatar>
                        <Avatar
                          sx={{ width: 28, height: 28, bgcolor: theme.palette.primary.light }}
                        >
                          <PhoneIcon fontSize="small" />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="body2" color="textSecondary">
                            Phone
                          </Typography>
                        }
                        secondary={<Link href={`tel:${rep.phone}`}>{rep.phone}</Link>}
                      />
                    </ListItem>
                  )}

                  {rep.website && (
                    <ListItem disablePadding sx={{ mb: 1 }}>
                      <ListItemAvatar>
                        <Avatar
                          sx={{ width: 28, height: 28, bgcolor: theme.palette.primary.light }}
                        >
                          <PublicIcon fontSize="small" />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="body2" color="textSecondary">
                            Website
                          </Typography>
                        }
                        secondary={
                          <Link
                            href={rep.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            sx={{
                              display: 'inline-block',
                              maxWidth: '100%',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {rep.website}
                          </Link>
                        }
                      />
                    </ListItem>
                  )}

                  {rep.address && (
                    <ListItem disablePadding>
                      <ListItemAvatar>
                        <Avatar
                          sx={{ width: 28, height: 28, bgcolor: theme.palette.primary.light }}
                        >
                          <LocationOnIcon fontSize="small" />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="body2" color="textSecondary">
                            Office
                          </Typography>
                        }
                        secondary={rep.address}
                      />
                    </ListItem>
                  )}
                </List>
              </CardContent>
              <CardActions sx={{ justifyContent: 'flex-end', p: 2, pt: 0 }}>
                <Button
                  size="small"
                  variant="outlined"
                  color="primary"
                  onClick={() => handleViewProjects(rep)}
                >
                  View Related Projects
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper
        elevation={2}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: 2,
          backgroundColor: theme.palette.background.paper,
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold" color="primary">
          Find Your Representatives
        </Typography>

        <Typography variant="body1" paragraph color="textSecondary">
          Enter your address to find representatives who serve your area. The list of your
          representatives will be stored in your browser for easy access to representative
          positions.
        </Typography>

        <form onSubmit={handleSubmit}>
          <Grid container spacing={2} alignItems="stretch">
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Street Address"
                variant="outlined"
                value={address}
                onChange={handleAddressChange}
                placeholder="123 Main St, City, IL 60601"
                required
                disabled={loading}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    height: '100%',
                  },
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                sx={{
                  height: '100%',
                  borderRadius: 2,
                  py: 1.5,
                }}
                disabled={loading}
                startIcon={
                  loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />
                }
              >
                {loading ? 'Searching...' : 'Find Representatives'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {searched && !loading && (
        <Fade in={searched}>
          <Box>
            <Box
              sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}
            >
              <Typography variant="h5" component="h2">
                Your Representatives
              </Typography>
              <Box>
                <Tooltip title="Representatives for your area">
                  <IconButton size="small" color="primary" sx={{ mr: 1 }}>
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Button variant="text" color="primary" onClick={clearSearch} size="small">
                  Clear Results
                </Button>
              </Box>
            </Box>

            {representatives.length > 0 && districts.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Districts:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {districts.map((district, index) => (
                    <Chip
                      key={index}
                      label={district}
                      color="secondary"
                      variant="outlined"
                      size="small"
                    />
                  ))}
                </Box>
              </Box>
            )}

            {renderRepresentativeCards(representatives)}
          </Box>
        </Fade>
      )}

      <Snackbar
        open={showToast}
        autoHideDuration={6000}
        onClose={handleCloseToast}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <MuiAlert elevation={6} variant="filled" onClose={handleCloseToast} severity="success">
          {toastMessage}
        </MuiAlert>
      </Snackbar>
    </Container>
  );
};

export default RepresentativeLookup;

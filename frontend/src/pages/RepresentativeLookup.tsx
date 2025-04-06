import React, { useState } from 'react';
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
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import PublicIcon from '@mui/icons-material/Public';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { Entity } from '../../types';
import { representativeService } from '../services/representatives';

const RepresentativeLookup: React.FC = () => {
  const [address, setAddress] = useState<string>('');
  const [representatives, setRepresentatives] = useState<Entity[]>([]);
  const [searched, setSearched] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddressChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setAddress(event.target.value);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await representativeService.findByAddress(address);
      setRepresentatives(response.data);
      setSearched(true);
    } catch (err) {
      setError('Failed to find representatives. Please try again.');
      console.error('Error fetching representatives:', err);
    } finally {
      setLoading(false);
    }
  };
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Find Your Representatives
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="body1" paragraph>
            Enter your address to find representatives who serve your area.
          </Typography>

          <form onSubmit={handleSubmit}>
            <Grid container spacing={2}>
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
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  fullWidth
                  sx={{ height: '56px' }}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Search'}
                </Button>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {searched && !loading && (
        <>
          <Typography variant="h5" gutterBottom>
            Your Representatives
          </Typography>

          {representatives.length > 0 ? (
            <Grid container spacing={3}>
              {representatives.map(rep => (
                <Grid item xs={12} md={6} key={rep.id}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" mb={2}>
                        <Avatar sx={{ mr: 2 }}>
                          <PersonIcon />
                        </Avatar>
                        <div>
                          <Typography variant="h6">{rep.name}</Typography>
                          <Typography variant="subtitle2" color="textSecondary">
                            {rep.title}
                          </Typography>
                          <Typography variant="subtitle1" color="textSecondary">
                            {rep.district_name}
                          </Typography>
                        </div>
                      </Box>

                      <Divider sx={{ mb: 2 }} />

                      <List dense>
                        {rep.email && (
                          <ListItem>
                            <ListItemAvatar>
                              <Avatar sx={{ width: 24, height: 24 }}>
                                <EmailIcon fontSize="small" />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                              primary="Email"
                              secondary={<Link href={`mailto:${rep.email}`}>{rep.email}</Link>}
                            />
                          </ListItem>
                        )}

                        {rep.phone && (
                          <ListItem>
                            <ListItemAvatar>
                              <Avatar sx={{ width: 24, height: 24 }}>
                                <PhoneIcon fontSize="small" />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                              primary="Phone"
                              secondary={<Link href={`tel:${rep.phone}`}>{rep.phone}</Link>}
                            />
                          </ListItem>
                        )}

                        {rep.website && (
                          <ListItem>
                            <ListItemAvatar>
                              <Avatar sx={{ width: 24, height: 24 }}>
                                <PublicIcon fontSize="small" />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                              primary="Website"
                              secondary={
                                <Link href={rep.website} target="_blank" rel="noopener noreferrer">
                                  {rep.website}
                                </Link>
                              }
                            />
                          </ListItem>
                        )}

                        {rep.address && (
                          <ListItem>
                            <ListItemAvatar>
                              <Avatar sx={{ width: 24, height: 24 }}>
                                <LocationOnIcon fontSize="small" />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText primary="Office" secondary={rep.address} />
                          </ListItem>
                        )}
                      </List>
                    </CardContent>
                    <CardActions>
                      <Button size="small" color="primary">
                        Related Projects
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography>No representatives found for this address.</Typography>
          )}
        </>
      )}
    </Container>
  );
};

export default RepresentativeLookup;

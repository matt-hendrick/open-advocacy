import React, { useState } from 'react';
import { 
  Container, Typography, TextField, Button, 
  Card, CardContent, CardActions, Grid, 
  List, ListItem, ListItemText, ListItemAvatar,
  Avatar, Link, Divider, Box
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import PublicIcon from '@mui/icons-material/Public';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { Entity } from '../../types';

// Mock data for now
const mockRepresentatives: Entity[] = [
  {
    id: "1",
    name: "Jane Doe",
    title: "City Council Member",
    entity_type: "alderman",
    jurisdiction_id: "ward-1",
    location_module_id: "chicago",
    contact_info: {
      email: "jane.doe@citycouncil.gov",
      phone: "(312) 555-1234",
      website: "https://www.citycouncil.gov/janedoe",
      address: "121 N LaSalle St, Chicago, IL 60602"
    }
  },
  {
    id: "2",
    name: "John Smith",
    title: "State Representative",
    entity_type: "state_rep",
    jurisdiction_id: "district-5",
    location_module_id: "illinois",
    contact_info: {
      email: "john.smith@ilga.gov",
      phone: "(217) 782-5678",
      website: "https://www.ilga.gov/house/johnsmith",
      address: "301 S 2nd St, Springfield, IL 62707"
    }
  }
];

const RepresentativeLookup: React.FC = () => {
  const [address, setAddress] = useState<string>('');
  const [representatives, setRepresentatives] = useState<Entity[]>([]);
  const [searched, setSearched] = useState<boolean>(false);

  const handleAddressChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setAddress(event.target.value);
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    // In a real app, we would call the API here
    setRepresentatives(mockRepresentatives);
    setSearched(true);
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
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Button 
                  type="submit" 
                  variant="contained" 
                  color="primary"
                  fullWidth
                  sx={{ height: '56px' }}
                >
                  Search
                </Button>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>
      
      {searched && (
        <>
          <Typography variant="h5" gutterBottom>
            Your Representatives
          </Typography>
          
          {representatives.length > 0 ? (
            <Grid container spacing={3}>
              {representatives.map((rep) => (
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
                        </div>
                      </Box>
                      
                      <Divider sx={{ mb: 2 }} />
                      
                      <List dense>
                        {rep.contact_info.email && (
                          <ListItem>
                            <ListItemAvatar>
                              <Avatar sx={{ width: 24, height: 24 }}>
                                <EmailIcon fontSize="small" />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText 
                              primary="Email" 
                              secondary={
                                <Link href={`mailto:${rep.contact_info.email}`}>
                                  {rep.contact_info.email}
                                </Link>
                              } 
                            />
                          </ListItem>
                        )}
                        
                        {rep.contact_info.phone && (
                          <ListItem>
                            <ListItemAvatar>
                              <Avatar sx={{ width: 24, height: 24 }}>
                                <PhoneIcon fontSize="small" />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText 
                              primary="Phone" 
                              secondary={
                                <Link href={`tel:${rep.contact_info.phone}`}>
                                  {rep.contact_info.phone}
                                </Link>
                              } 
                            />
                          </ListItem>
                        )}
                        
                        {rep.contact_info.website && (
                          <ListItem>
                            <ListItemAvatar>
                              <Avatar sx={{ width: 24, height: 24 }}>
                                <PublicIcon fontSize="small" />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText 
                              primary="Website" 
                              secondary={
                                <Link href={rep.contact_info.website} target="_blank" rel="noopener noreferrer">
                                  {rep.contact_info.website}
                                </Link>
                              } 
                            />
                          </ListItem>
                        )}
                        
                        {rep.contact_info.address && (
                          <ListItem>
                            <ListItemAvatar>
                              <Avatar sx={{ width: 24, height: 24 }}>
                                <LocationOnIcon fontSize="small" />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText 
                              primary="Office" 
                              secondary={rep.contact_info.address} 
                            />
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
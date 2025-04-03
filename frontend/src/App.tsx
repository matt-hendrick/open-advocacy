import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';

// Components
import Header from './components/common/Header';

// Pages
import HomePage from './pages/HomePage';
import ProjectList from './components/Project/ProjectList';
import RepresentativeLookup from './components/Entity/RepresentativeLookup';

// Create a theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Header />
        <main style={{ padding: '2rem 0' }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/projects" element={<ProjectList />} />
            <Route path="/representatives" element={<RepresentativeLookup />} />
          </Routes>
        </main>
      </Router>
    </ThemeProvider>
  );
};

export default App;
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './theme/ThemeProvider';
import { UserRepresentativesProvider } from './contexts/UserRepresentativesContext';

import Header from './components/common/Header';
import HomePage from './pages/HomePage';
import ProjectDetail from './pages/ProjectDetail';
import ProjectFormPage from './pages/ProjectFormPage';
import ProjectList from './pages/ProjectList';
import RepresentativeLookup from './pages/RepresentativeLookup';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <UserRepresentativesProvider>
        <Router>
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/projects" element={<ProjectList />} />
              <Route path="/projects/create" element={<ProjectFormPage />} />
              <Route path="/projects/:id/edit" element={<ProjectFormPage />} />
              <Route path="/projects/:id" element={<ProjectDetail />} />
              <Route path="/representatives" element={<RepresentativeLookup />} />
            </Routes>
          </main>
        </Router>
      </UserRepresentativesProvider>
    </ThemeProvider>
  );
};

export default App;

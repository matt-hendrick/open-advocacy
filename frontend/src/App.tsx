// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './theme/ThemeProvider';
import Header from './components/common/Header';
import HomePage from './pages/HomePage';
import ProjectList from './components/Project/ProjectList';
import RepresentativeLookup from './components/Entity/RepresentativeLookup';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <Router>
        <Header />
        <main>
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
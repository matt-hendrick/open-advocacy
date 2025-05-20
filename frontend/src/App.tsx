import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './theme/ThemeProvider';
import { AuthProvider } from './contexts/AuthContext';
import { UserRepresentativesProvider } from './contexts/UserRepresentativesContext';

import Header from './components/common/Header';
import HomePage from './pages/HomePage';
import ProjectDetail from './pages/ProjectDetail';
import ProjectFormPage from './pages/ProjectFormPage';
import ProjectList from './pages/ProjectList';
import RepresentativeLookup from './pages/RepresentativeLookup';
import EntityDetail from './pages/EntityDetail';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UnauthorizedPage from './pages/UnauthorizedPage';

import ProtectedRoute from './components/auth/ProtectedRoute';

const App: React.FC = () => {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <UserRepresentativesProvider>
            <Header />
            <main>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/projects" element={<ProjectList />} />
                <Route path="/projects/create" element={<ProjectFormPage />} />
                <Route path="/projects/:id/edit" element={<ProjectFormPage />} />
                <Route path="/projects/:id" element={<ProjectDetail />} />
                <Route path="/representatives" element={<RepresentativeLookup />} />
                <Route path="/representatives/:id" element={<EntityDetail />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/unauthorized" element={<UnauthorizedPage />} />

                <Route
                  path="/register"
                  element={
                    <ProtectedRoute requiredRoles={['super_admin', 'group_admin']}>
                      <RegisterPage />
                    </ProtectedRoute>
                  }
                />

                {/* TODO: Add Admin routes */}
                <Route
                  path="/admin/*"
                  element={
                    <ProtectedRoute requiredRoles={['super_admin', 'group_admin']}>
                      {/* TODO: Add Admin component */}
                      <div>Admin Panel</div>
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </main>
          </UserRepresentativesProvider>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
};

export default App;

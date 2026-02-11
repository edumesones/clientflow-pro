import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Calendar from './pages/Calendar';
import Leads from './pages/Leads';
import PublicBooking from './pages/PublicBooking';
import NotFound from './pages/NotFound';

// Protected Route component
const ProtectedRoute = ({ children, requireProfessional = true }) => {
  const { user, loading, isProfessional } = useAuth();
  
  if (loading) return <div>Cargando...</div>;
  if (!user) return <Navigate to="/login" />;
  if (requireProfessional && !isProfessional()) return <Navigate to="/" />;
  
  return children;
};

// Admin Layout
const AdminLayout = ({ children }) => {
  return (
    <div className="admin-layout">
      <Sidebar />
      <main className="admin-content">
        {children}
      </main>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <Navbar />
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/book/:slug" element={<PublicBooking />} />
        
        {/* Protected Admin Routes */}
        <Route path="/admin" element={
          <ProtectedRoute>
            <AdminLayout>
              <Dashboard />
            </AdminLayout>
          </ProtectedRoute>
        } />
        <Route path="/admin/calendar" element={
          <ProtectedRoute>
            <AdminLayout>
              <Calendar />
            </AdminLayout>
          </ProtectedRoute>
        } />
        <Route path="/admin/leads" element={
          <ProtectedRoute>
            <AdminLayout>
              <Leads />
            </AdminLayout>
          </ProtectedRoute>
        } />
        
        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/admin" />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  );
}

export default App;

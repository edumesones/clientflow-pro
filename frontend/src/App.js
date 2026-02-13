import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Calendar from './pages/CalendarPage';
import AppointmentsPage from './pages/AppointmentsPage';
import LeadsPage from './pages/LeadsPage';
import AvailabilityPage from './pages/AvailabilityPage';
import ProfilePage from './pages/ProfilePage';
import ClientsPage from './pages/ClientsPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  const { user, loading } = useAuth();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="loading-screen" style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: '#f5f7fa'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div className="spinner" style={{
            width: '40px',
            height: '40px',
            border: '4px solid #e5e7eb',
            borderTop: '4px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }} />
          <p style={{ color: '#6b7280' }}>Cargando...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    );
  }

  return (
    <div className="app">
      <Navbar />
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/appointments" element={<AppointmentsPage />} />
            <Route path="/leads" element={<LeadsPage />} />
            <Route path="/availability" element={<AvailabilityPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/clients" element={<ClientsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;

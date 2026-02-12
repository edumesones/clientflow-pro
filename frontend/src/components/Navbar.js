import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout, isProfessional } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">ClientFlow Pro</Link>
      </div>
      
      <div className="navbar-links">
        {user ? (
          <>
            {isProfessional() && (
              <>
                <Link to="/dashboard">Dashboard</Link>
                <Link to="/calendar">Calendario</Link>
              </>
            )}
            <div className="navbar-user">
              <span>{user.full_name}</span>
              <button onClick={handleLogout} className="btn-logout">
                Cerrar sesión
              </button>
            </div>
          </>
        ) : (
          <>
            <Link to="/login">Iniciar sesión</Link>
            <Link to="/register" className="btn-primary">Registrarse</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;

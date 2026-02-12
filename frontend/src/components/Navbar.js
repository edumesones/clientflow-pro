import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout, isProfessional } = useAuth();
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showDropdown]);

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
            <div className="navbar-user" ref={dropdownRef}>
              <button
                className="user-menu-button"
                onClick={() => setShowDropdown(!showDropdown)}
              >
                <div className="user-avatar">
                  {user.full_name.charAt(0).toUpperCase()}
                </div>
                <span className="user-name">{user.full_name}</span>
                <span className="dropdown-arrow">{showDropdown ? '▲' : '▼'}</span>
              </button>

              {showDropdown && (
                <div className="user-dropdown">
                  <Link
                    to="/profile"
                    className="dropdown-item"
                    onClick={() => setShowDropdown(false)}
                  >
                    <span className="dropdown-icon">👤</span>
                    Mi Perfil
                  </Link>
                  <Link
                    to="/settings"
                    className="dropdown-item"
                    onClick={() => setShowDropdown(false)}
                  >
                    <span className="dropdown-icon">⚙️</span>
                    Configuración
                  </Link>
                  <div className="dropdown-divider"></div>
                  <button
                    onClick={() => {
                      setShowDropdown(false);
                      handleLogout();
                    }}
                    className="dropdown-item dropdown-logout"
                  >
                    <span className="dropdown-icon">🚪</span>
                    Cerrar sesión
                  </button>
                </div>
              )}
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

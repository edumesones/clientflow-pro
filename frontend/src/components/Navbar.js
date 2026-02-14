import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout, isProfessional } = useAuth();
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const dropdownRef = useRef(null);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close dropdown when clicking outside
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

  // Close dropdown on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [showDropdown]);

  return (
    <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`}>
      <div className="navbar-container">
        {/* Brand */}
        <div className="navbar-brand">
          <Link to="/" className="brand-link">
            <span className="brand-icon">🌿</span>
            <span className="brand-text">ClientFlow Pro</span>
          </Link>
        </div>
        
        {/* Navigation Links */}
        <div className="navbar-links">
          {user ? (
            <>
              {/* Desktop Navigation Links */}
              <div className="desktop-nav-links">
                {isProfessional() && (
                  <>
                    <Link to="/dashboard" className="nav-link">Dashboard</Link>
                    <Link to="/calendar" className="nav-link">Calendario</Link>
                    <Link to="/appointments" className="nav-link">Citas</Link>
                  </>
                )}
              </div>

              {/* User Menu */}
              <div className="navbar-user" ref={dropdownRef}>
                <button
                  className={`user-menu-button ${showDropdown ? 'active' : ''}`}
                  onClick={() => setShowDropdown(!showDropdown)}
                  aria-expanded={showDropdown}
                  aria-haspopup="true"
                >
                  <div className="user-avatar">
                    {user.full_name?.charAt(0).toUpperCase() || '?'}
                  </div>
                  <span className="user-name desktop-only">{user.full_name}</span>
                  <svg 
                    className={`dropdown-chevron ${showDropdown ? 'open' : ''}`}
                    width="12" 
                    height="12" 
                    viewBox="0 0 12 12"
                    fill="none"
                    aria-hidden="true"
                  >
                    <path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>

                {/* Dropdown Menu */}
                {showDropdown && (
                  <div className="user-dropdown">
                    <div className="dropdown-header">
                      <div className="dropdown-user-name">{user.full_name}</div>
                      <div className="dropdown-user-email">{user.email}</div>
                    </div>
                    <div className="dropdown-divider"></div>
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
            <div className="auth-links">
              <Link to="/login" className="nav-link">Iniciar sesión</Link>
              <Link to="/register" className="btn btn-primary btn-register">Registrarse</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

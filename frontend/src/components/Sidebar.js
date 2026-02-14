import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 1024);

  const menuItems = [
    { path: '/dashboard', icon: '📊', label: 'Dashboard' },
    { path: '/calendar', icon: '📅', label: 'Calendario' },
    { path: '/appointments', icon: '📆', label: 'Citas' },
    { path: '/leads', icon: '🎯', label: 'Leads' },
    { path: '/clients', icon: '👥', label: 'Clientes' },
    { path: '/availability', icon: '🕐', label: 'Horarios' },
    { path: '/profile', icon: '👤', label: 'Mi Perfil' },
    { path: '/settings', icon: '⚙️', label: 'Configuración' },
  ];

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 1024;
      setIsMobile(mobile);
      if (!mobile) {
        setIsOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Close menu when route changes on mobile
  useEffect(() => {
    if (isMobile) {
      setIsOpen(false);
    }
  }, [location.pathname, isMobile]);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isOpen && isMobile) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen, isMobile]);

  const toggleMenu = () => setIsOpen(!isOpen);

  return (
    <>
      {/* Mobile Menu Button */}
      {isMobile && (
        <button
          className={`mobile-menu-btn ${isOpen ? 'open' : ''}`}
          onClick={toggleMenu}
          aria-label={isOpen ? 'Cerrar menú' : 'Abrir menú'}
          aria-expanded={isOpen}
        >
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
        </button>
      )}

      {/* Mobile Menu Overlay */}
      {isMobile && (
        <div
          className={`mobile-menu-overlay ${isOpen ? 'open' : ''}`}
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${isMobile ? 'mobile' : 'desktop'} ${isOpen ? 'open' : ''}`}>
        {/* Mobile Sidebar Header */}
        {isMobile && (
          <div className="sidebar-header">
            <span className="sidebar-logo">ClientFlow Pro</span>
          </div>
        )}

        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-link ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => isMobile && setIsOpen(false)}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span className="sidebar-label">{item.label}</span>
              {location.pathname === item.path && (
                <span className="active-indicator" aria-hidden="true"></span>
              )}
            </Link>
          ))}
        </nav>

        {/* Mobile Sidebar Footer */}
        {isMobile && (
          <div className="sidebar-footer">
            <p className="sidebar-version">v2.0.0</p>
          </div>
        )}
      </aside>
    </>
  );
};

export default Sidebar;

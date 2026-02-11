import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => {
  const location = useLocation();
  
  const menuItems = [
    { path: '/admin', icon: '📊', label: 'Dashboard' },
    { path: '/admin/calendar', icon: '📅', label: 'Calendario' },
    { path: '/admin/appointments', icon: '📆', label: 'Citas' },
    { path: '/admin/leads', icon: '🎯', label: 'Leads' },
    { path: '/admin/clients', icon: '👥', label: 'Clientes' },
    { path: '/admin/settings', icon: '⚙️', label: 'Configuración' },
  ];

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`sidebar-link ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="sidebar-icon">{item.icon}</span>
            <span className="sidebar-label">{item.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;

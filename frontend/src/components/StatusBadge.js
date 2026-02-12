import React from 'react';
import './StatusBadge.css';

const StatusBadge = ({ status, type = 'appointment' }) => {
  // Status configurations for different entity types
  const statusConfig = {
    appointment: {
      pending: { label: 'Pendiente', className: 'status-pending' },
      confirmed: { label: 'Confirmada', className: 'status-confirmed' },
      completed: { label: 'Completada', className: 'status-completed' },
      cancelled: { label: 'Cancelada', className: 'status-cancelled' },
      no_show: { label: 'No asistió', className: 'status-noshow' },
    },
    lead: {
      nuevo: { label: 'Nuevo', className: 'status-new' },
      new: { label: 'Nuevo', className: 'status-new' },
      contactado: { label: 'Contactado', className: 'status-contacted' },
      contacted: { label: 'Contactado', className: 'status-contacted' },
      convertido: { label: 'Convertido', className: 'status-converted' },
      converted: { label: 'Convertido', className: 'status-converted' },
      perdido: { label: 'Perdido', className: 'status-lost' },
      lost: { label: 'Perdido', className: 'status-lost' },
    },
    client: {
      active: { label: 'Activo', className: 'status-active' },
      activo: { label: 'Activo', className: 'status-active' },
      inactive: { label: 'Inactivo', className: 'status-inactive' },
      inactivo: { label: 'Inactivo', className: 'status-inactive' },
      vip: { label: 'VIP', className: 'status-vip' },
    },
  };

  const config = statusConfig[type]?.[status?.toLowerCase()] || {
    label: status || 'Desconocido',
    className: 'status-default',
  };

  return (
    <span
      className={`status-badge ${config.className}`}
      aria-label={`Estado: ${config.label}`}
    >
      {config.label}
    </span>
  );
};

export default StatusBadge;

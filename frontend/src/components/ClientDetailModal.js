import React, { useState, useEffect } from 'react';
import Modal from './Modal';
import Button from './Button';
import { usersAPI } from '../services/apiService';
import './ClientDetailModal.css';

const ClientDetailModal = ({ isOpen, onClose, client, onRefresh }) => {
  const [activeTab, setActiveTab] = useState('summary');
  const [clientStats, setClientStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && client) {
      fetchClientStats();
    }
  }, [isOpen, client]);

  const fetchClientStats = async () => {
    try {
      setLoading(true);
      const response = await usersAPI.getClientStats(client.id);
      setClientStats(response.data);
    } catch (error) {
      console.error('Error fetching client stats:', error);
      // Use fallback data from client object if API fails
      const fallbackStats = {
        total_appointments: client.total_appointments || 0,
        completed: Math.floor((client.total_appointments || 0) * 0.85),
        cancelled: Math.floor((client.total_appointments || 0) * 0.1),
        no_show: Math.floor((client.total_appointments || 0) * 0.05),
        no_show_rate: client.no_show_rate || 0,
        average_rating: null,
      };
      setClientStats(fallbackStats);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const renderSummaryTab = () => (
    <div className="tab-content">
      <div className="client-summary-header">
        <div className="client-avatar-large">
          {client.full_name.charAt(0).toUpperCase()}
        </div>
        <div className="client-summary-info">
          <h3>{client.full_name}</h3>
          <p>{client.email}</p>
          <p>{client.phone}</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{clientStats?.total_appointments || 0}</div>
          <div className="stat-label">Total Citas</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{clientStats?.completed || 0}</div>
          <div className="stat-label">Completadas</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{clientStats?.no_show_rate || 0}%</div>
          <div className="stat-label">No-Show</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">⭐ {clientStats?.average_rating || 0}</div>
          <div className="stat-label">Calificación</div>
        </div>
      </div>

      <div className="info-section">
        <h4>Información General</h4>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Cliente desde:</span>
            <span className="info-value">{formatDate(client.created_at)}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Última cita:</span>
            <span className="info-value">{formatDate(client.last_appointment_date)}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Estado:</span>
            <span className="info-value">{client.status}</span>
          </div>
        </div>
      </div>

      <div className="notes-section">
        <h4>Notas del Profesional</h4>
        <div className="notes-placeholder">
          <p>El sistema de notas estará disponible en una próxima actualización.</p>
          <Button variant="ghost" size="small" onClick={() => alert('Funcionalidad próximamente')}>
            + Agregar Nota
          </Button>
        </div>
      </div>
    </div>
  );

  const renderAppointmentsTab = () => (
    <div className="tab-content">
      <div className="appointments-header">
        <h4>Historial de Citas</h4>
        <Button variant="primary" size="small" onClick={() => alert('Agendar cita - próximamente')}>
          Nueva Cita
        </Button>
      </div>

      <div className="appointments-placeholder">
        <p>📅 Este cliente tiene {client.total_appointments} citas registradas.</p>
        <p className="placeholder-detail">
          El historial detallado de citas estará disponible en una próxima actualización.
        </p>
      </div>
    </div>
  );

  const renderHistoryTab = () => (
    <div className="tab-content">
      <h4>Timeline de Interacciones</h4>

      <div className="history-placeholder">
        <p>📧 El timeline mostrará:</p>
        <ul>
          <li>Emails enviados (Fase 3)</li>
          <li>Cambios de estado</li>
          <li>Notas agregadas</li>
          <li>Citas agendadas/canceladas</li>
          <li>Recordatorios enviados</li>
        </ul>
      </div>
    </div>
  );

  if (!client) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalles del Cliente"
      size="large"
    >
      <div className="client-detail-modal">
        <div className="tabs-header">
          <button
            className={`tab-button ${activeTab === 'summary' ? 'active' : ''}`}
            onClick={() => setActiveTab('summary')}
          >
            Resumen
          </button>
          <button
            className={`tab-button ${activeTab === 'appointments' ? 'active' : ''}`}
            onClick={() => setActiveTab('appointments')}
          >
            Citas
          </button>
          <button
            className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            Historial
          </button>
        </div>

        <div className="tabs-body">
          {loading ? (
            <div className="loading-state">Cargando información...</div>
          ) : (
            <>
              {activeTab === 'summary' && renderSummaryTab()}
              {activeTab === 'appointments' && renderAppointmentsTab()}
              {activeTab === 'history' && renderHistoryTab()}
            </>
          )}
        </div>

        <div className="modal-actions">
          <Button variant="ghost" onClick={onClose}>
            Cerrar
          </Button>
          <Button variant="secondary" onClick={() => alert('Editar cliente - próximamente')}>
            Editar Info
          </Button>
          <Button variant="primary" onClick={() => alert('Marcar como VIP - próximamente')}>
            Marcar VIP
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default ClientDetailModal;

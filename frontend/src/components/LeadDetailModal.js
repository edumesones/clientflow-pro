import React, { useState } from 'react';
import Modal from './Modal';
import Button from './Button';
import StatusBadge from './StatusBadge';
import { leadsAPI } from '../services/apiService';
import './LeadDetailModal.css';

const LeadDetailModal = ({
  isOpen,
  onClose,
  lead,
  onEdit,
  onDelete,
  onRefresh,
  onConvertToAppointment,
}) => {
  const [updating, setUpdating] = useState(false);

  if (!lead) return null;

  const handleMarkContacted = async () => {
    if (updating) return;

    try {
      setUpdating(true);
      await leadsAPI.markContacted(lead.id);
      onRefresh();
      onClose();
    } catch (error) {
      console.error('Error marking as contacted:', error);
      alert('Error al marcar como contactado');
    } finally {
      setUpdating(false);
    }
  };

  const handleConvert = () => {
    if (onConvertToAppointment) {
      onConvertToAppointment(lead);
    }
    onClose();
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalles del Lead"
      size="medium"
    >
      <div className="lead-detail">
        <div className="detail-header">
          <div className="lead-info">
            <h2 className="lead-name">{lead.name}</h2>
            <p className="lead-contact">
              {lead.email} • {lead.phone}
            </p>
          </div>
          <StatusBadge status={lead.status} type="lead" />
        </div>

        <div className="detail-section">
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Fuente:</span>
              <span className="detail-value">{lead.source}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Estado:</span>
              <span className="detail-value">
                {lead.status === 'new' && 'Nuevo'}
                {lead.status === 'contacted' && 'Contactado'}
                {lead.status === 'converted' && 'Convertido'}
                {lead.status === 'lost' && 'Perdido'}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Creado:</span>
              <span className="detail-value">
                {formatDate(lead.created_at)}
              </span>
            </div>

            {lead.updated_at && (
              <div className="detail-item">
                <span className="detail-label">Última actualización:</span>
                <span className="detail-value">
                  {formatDate(lead.updated_at)}
                </span>
              </div>
            )}
          </div>

          {lead.message && (
            <div className="message-section">
              <span className="detail-label">Mensaje:</span>
              <p className="message-text">{lead.message}</p>
            </div>
          )}
        </div>

        <div className="detail-section timeline-placeholder">
          <h3 className="section-title">📧 Timeline de Interacciones</h3>
          <p className="placeholder-text">
            El historial de seguimiento automático estará disponible en la próxima versión
          </p>
        </div>

        <div className="detail-actions">
          <div className="status-actions">
            {lead.status === 'new' && (
              <Button
                variant="success"
                size="small"
                onClick={handleMarkContacted}
                loading={updating}
              >
                Marcar Contactado
              </Button>
            )}
            {(lead.status === 'new' || lead.status === 'contacted') && onConvertToAppointment && (
              <Button
                variant="primary"
                size="small"
                onClick={handleConvert}
              >
                Convertir a Cita
              </Button>
            )}
          </div>

          <div className="main-actions">
            <Button variant="ghost" onClick={() => onEdit(lead)}>
              Editar
            </Button>
            <Button variant="danger" onClick={() => onDelete(lead.id)}>
              Eliminar
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default LeadDetailModal;

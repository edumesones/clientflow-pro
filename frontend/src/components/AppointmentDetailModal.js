import React, { useState } from 'react';
import Modal from './Modal';
import Button from './Button';
import StatusBadge from './StatusBadge';
import { appointmentsAPI } from '../services/apiService';
import './AppointmentDetailModal.css';

const AppointmentDetailModal = ({
  isOpen,
  onClose,
  appointment,
  onEdit,
  onDelete,
  onRefresh,
}) => {
  const [updating, setUpdating] = useState(false);

  if (!appointment) return null;

  const handleStatusChange = async (newStatus) => {
    if (updating) return;

    try {
      setUpdating(true);
      await appointmentsAPI.update(appointment.id, { status: newStatus });
      onRefresh();
      onClose();
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Error al actualizar el estado');
    } finally {
      setUpdating(false);
    }
  };

  const handleCancel = () => {
    onDelete(appointment.id);
  };

  const handleEdit = () => {
    onEdit(appointment);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalles de la Cita"
      size="large"
    >
      <div className="appointment-detail">
        {/* Header with client info */}
        <div className="detail-header">
          <div className="client-info">
            <h2 className="client-name">{appointment.client_name}</h2>
            <p className="client-contact">
              {appointment.client_email}
              {appointment.client_phone && ` • ${appointment.client_phone}`}
            </p>
          </div>
          <StatusBadge status={appointment.status} type="appointment" />
        </div>

        {/* Appointment details */}
        <div className="detail-section">
          <h3 className="section-title">Información de la Cita</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Servicio:</span>
              <span className="detail-value">
                {appointment.service_type || 'Consulta general'}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Fecha:</span>
              <span className="detail-value">
                {formatDate(appointment.appointment_date)}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Hora:</span>
              <span className="detail-value">{appointment.start_time}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Duración:</span>
              <span className="detail-value">{appointment.duration} minutos</span>
            </div>

            {appointment.price && (
              <div className="detail-item">
                <span className="detail-label">Precio:</span>
                <span className="detail-value">${appointment.price}</span>
              </div>
            )}

            <div className="detail-item">
              <span className="detail-label">Estado:</span>
              <span className="detail-value">
                {appointment.status === 'pending' && 'Pendiente de confirmación'}
                {appointment.status === 'confirmed' && 'Confirmada'}
                {appointment.status === 'completed' && 'Completada'}
                {appointment.status === 'cancelled' && 'Cancelada'}
                {appointment.status === 'no_show' && 'Cliente no asistió'}
              </span>
            </div>
          </div>

          {appointment.notes && (
            <div className="notes-section">
              <span className="detail-label">Notas:</span>
              <p className="notes-text">{appointment.notes}</p>
            </div>
          )}
        </div>

        {/* Brief section - placeholder for Phase 3 */}
        <div className="detail-section brief-placeholder">
          <h3 className="section-title">📋 Brief IA</h3>
          <p className="placeholder-text">
            El brief inteligente estará disponible en la próxima versión
          </p>
        </div>

        {/* Actions */}
        <div className="detail-actions">
          <div className="status-actions">
            {appointment.status === 'pending' && (
              <Button
                variant="success"
                size="small"
                onClick={() => handleStatusChange('confirmed')}
                loading={updating}
              >
                Confirmar
              </Button>
            )}
            {(appointment.status === 'confirmed' || appointment.status === 'pending') && (
              <>
                <Button
                  variant="primary"
                  size="small"
                  onClick={() => handleStatusChange('completed')}
                  loading={updating}
                >
                  Marcar Completada
                </Button>
                <Button
                  variant="secondary"
                  size="small"
                  onClick={() => handleStatusChange('no_show')}
                  loading={updating}
                >
                  No Asistió
                </Button>
              </>
            )}
          </div>

          <div className="main-actions">
            <Button variant="ghost" onClick={handleEdit}>
              Editar
            </Button>
            {appointment.status !== 'cancelled' && (
              <Button variant="danger" onClick={handleCancel}>
                Cancelar Cita
              </Button>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default AppointmentDetailModal;

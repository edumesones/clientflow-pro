import React, { useState, useEffect, useCallback } from 'react';
import Calendar from 'react-calendar';
import { appointmentsAPI } from '../services/apiService';
import AppointmentForm from '../components/AppointmentForm';
import AppointmentDetailModal from '../components/AppointmentDetailModal';
import Button from '../components/Button';
import 'react-calendar/dist/Calendar.css';
import './CalendarPage.css';

const CalendarPage = () => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAppointmentForm, setShowAppointmentForm] = useState(false);
  const [showAppointmentDetail, setShowAppointmentDetail] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [formMode, setFormMode] = useState('create');

  const fetchAppointments = useCallback(async () => {
    try {
      const startOfMonth = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1);
      const endOfMonth = new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1, 0);
      
      const response = await appointmentsAPI.getAll({
        start_date: startOfMonth.toISOString().split('T')[0],
        end_date: endOfMonth.toISOString().split('T')[0],
      });
      
      setAppointments(response.data);
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedDate]);

  useEffect(() => {
    fetchAppointments();
  }, [fetchAppointments]);

  const getAppointmentsForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return appointments.filter(appt => appt.appointment_date === dateStr);
  };

  const handleDateClick = (date) => {
    setSelectedDate(date);
  };

  const handleNewAppointment = () => {
    setSelectedAppointment(null);
    setFormMode('create');
    setShowAppointmentForm(true);
  };

  const handleAppointmentClick = (appointment) => {
    setSelectedAppointment(appointment);
    setShowAppointmentDetail(true);
  };

  const handleEditAppointment = (appointment) => {
    setSelectedAppointment(appointment);
    setFormMode('edit');
    setShowAppointmentDetail(false);
    setShowAppointmentForm(true);
  };

  const handleDeleteAppointment = async (appointmentId) => {
    if (window.confirm('¿Estás seguro de que deseas cancelar esta cita?')) {
      try {
        await appointmentsAPI.cancel(appointmentId);
        fetchAppointments();
      } catch (error) {
        console.error('Error canceling appointment:', error);
        alert('Error al cancelar la cita');
      }
    }
  };

  const handleFormSuccess = () => {
    setShowAppointmentForm(false);
    setSelectedAppointment(null);
    fetchAppointments();
  };

  const tileContent = ({ date, view }) => {
    if (view === 'month') {
      const dayAppointments = getAppointmentsForDate(date);
      if (dayAppointments.length > 0) {
        return (
          <div className="calendar-dots">
            {dayAppointments.slice(0, 3).map((appt, idx) => (
              <span 
                key={idx} 
                className={`dot dot-${appt.status}`}
              />
            ))}
            {dayAppointments.length > 3 && <span className="dot-more">+</span>}
          </div>
        );
      }
    }
    return null;
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="calendar-page">
      <div className="calendar-header">
        <h1>Calendario de Citas</h1>
        <Button variant="primary" onClick={handleNewAppointment}>
          Nueva Cita
        </Button>
      </div>
      
      <div className="calendar-container">
        <div className="calendar-wrapper">
          <Calendar
            onChange={handleDateClick}
            value={selectedDate}
            tileContent={tileContent}
            className="custom-calendar"
          />
          
          <div className="calendar-legend">
            <div className="legend-item">
              <span className="dot dot-confirmed"></span>
              <span>Confirmada</span>
            </div>
            <div className="legend-item">
              <span className="dot dot-pending"></span>
              <span>Pendiente</span>
            </div>
            <div className="legend-item">
              <span className="dot dot-completed"></span>
              <span>Completada</span>
            </div>
            <div className="legend-item">
              <span className="dot dot-cancelled"></span>
              <span>Cancelada</span>
            </div>
          </div>
        </div>

        <div className="appointments-sidebar">
          <h2>{formatDate(selectedDate)}</h2>
          
          {loading ? (
            <p>Cargando...</p>
          ) : (
            <div className="day-appointments">
              {getAppointmentsForDate(selectedDate).length === 0 ? (
                <p className="no-appointments">No hay citas para este día</p>
              ) : (
                getAppointmentsForDate(selectedDate).map((appt) => (
                  <div
                    key={appt.id}
                    className={`day-appointment-item status-${appt.status} clickable`}
                    onClick={() => handleAppointmentClick(appt)}
                  >
                    <div className="appointment-time">{appt.start_time}</div>
                    <div className="appointment-details">
                      <h4>{appt.client?.full_name || appt.lead_name || 'Sin nombre'}</h4>
                      <p>{appt.service_type || 'Consulta general'}</p>
                    </div>
                    <span className={`status-badge status-${appt.status}`}>
                      {appt.status}
                    </span>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {showAppointmentForm && (
        <AppointmentForm
          isOpen={showAppointmentForm}
          onClose={() => {
            setShowAppointmentForm(false);
            setSelectedAppointment(null);
          }}
          appointment={formMode === 'edit' ? selectedAppointment : null}
          initialDate={selectedDate.toISOString().split('T')[0]}
          onSuccess={handleFormSuccess}
        />
      )}

      {selectedAppointment && showAppointmentDetail && (
        <AppointmentDetailModal
          isOpen={showAppointmentDetail}
          onClose={() => {
            setShowAppointmentDetail(false);
            setSelectedAppointment(null);
          }}
          appointment={selectedAppointment}
          onEdit={() => handleEditAppointment(selectedAppointment)}
          onDelete={() => handleDeleteAppointment(selectedAppointment.id)}
          onRefresh={fetchAppointments}
        />
      )}
    </div>
  );
};

export default CalendarPage;

import React, { useState, useEffect } from 'react';
import FormField from './FormField';
import Button from './Button';
import { appointmentsAPI, availabilityAPI } from '../services/apiService';
import './AppointmentForm.css';

const AppointmentForm = ({ appointment, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    client_name: '',
    client_email: '',
    client_phone: '',
    service_type: '',
    appointment_date: '',
    start_time: '',
    duration: 60,
    notes: '',
    price: '',
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);

  useEffect(() => {
    if (appointment) {
      setFormData({
        client_name: appointment.client_name || '',
        client_email: appointment.client_email || '',
        client_phone: appointment.client_phone || '',
        service_type: appointment.service_type || '',
        appointment_date: appointment.appointment_date || '',
        start_time: appointment.start_time || '',
        duration: appointment.duration || 60,
        notes: appointment.notes || '',
        price: appointment.price || '',
      });
    }
  }, [appointment]);

  useEffect(() => {
    if (formData.appointment_date) {
      fetchAvailableSlots();
    }
  }, [formData.appointment_date]);

  const fetchAvailableSlots = async () => {
    try {
      setLoadingSlots(true);
      // Note: This endpoint needs professional_id, we're using a placeholder
      // In real implementation, get current professional from auth context
      const response = await availabilityAPI.getAvailable(1, formData.appointment_date);
      setAvailableSlots(response.data || []);
    } catch (error) {
      console.error('Error fetching slots:', error);
      setAvailableSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.client_name.trim()) {
      newErrors.client_name = 'El nombre del cliente es requerido';
    }

    if (!formData.client_email.trim()) {
      newErrors.client_email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.client_email)) {
      newErrors.client_email = 'Email inválido';
    }

    if (!formData.appointment_date) {
      newErrors.appointment_date = 'La fecha es requerida';
    } else {
      const selectedDate = new Date(formData.appointment_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (selectedDate < today) {
        newErrors.appointment_date = 'La fecha debe ser futura';
      }
    }

    if (!formData.start_time) {
      newErrors.start_time = 'La hora es requerida';
    }

    if (!formData.service_type.trim()) {
      newErrors.service_type = 'El tipo de servicio es requerido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setLoading(true);

    try {
      const data = {
        ...formData,
        duration: parseInt(formData.duration),
        price: formData.price ? parseFloat(formData.price) : null,
      };

      if (appointment) {
        await appointmentsAPI.update(appointment.id, data);
      } else {
        await appointmentsAPI.create(data);
      }

      onSuccess();
    } catch (error) {
      console.error('Error saving appointment:', error);
      const errorMessage = error.response?.data?.detail || 'Error al guardar la cita';
      setErrors({ submit: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="appointment-form">
      {errors.submit && (
        <div className="form-error-banner">
          {errors.submit}
        </div>
      )}

      <div className="form-section">
        <h3 className="section-title">Información del Cliente</h3>
        <div className="form-row">
          <FormField
            label="Nombre completo"
            name="client_name"
            value={formData.client_name}
            onChange={handleChange}
            error={errors.client_name}
            required
            autoFocus
          />

          <FormField
            label="Email"
            type="email"
            name="client_email"
            value={formData.client_email}
            onChange={handleChange}
            error={errors.client_email}
            required
          />
        </div>

        <FormField
          label="Teléfono"
          type="tel"
          name="client_phone"
          value={formData.client_phone}
          onChange={handleChange}
          error={errors.client_phone}
          placeholder="555-123-4567"
        />
      </div>

      <div className="form-section">
        <h3 className="section-title">Detalles de la Cita</h3>
        <FormField
          label="Tipo de servicio"
          name="service_type"
          value={formData.service_type}
          onChange={handleChange}
          error={errors.service_type}
          required
          placeholder="Ej: Consulta inicial, Seguimiento, etc."
        />

        <div className="form-row">
          <FormField
            label="Fecha"
            type="date"
            name="appointment_date"
            value={formData.appointment_date}
            onChange={handleChange}
            error={errors.appointment_date}
            required
            min={new Date().toISOString().split('T')[0]}
          />

          <FormField
            label="Hora"
            type="time"
            name="start_time"
            value={formData.start_time}
            onChange={handleChange}
            error={errors.start_time}
            required
          />
        </div>

        {loadingSlots && (
          <div className="slots-loading">Cargando horarios disponibles...</div>
        )}

        <div className="form-row">
          <FormField
            label="Duración (minutos)"
            type="select"
            name="duration"
            value={formData.duration}
            onChange={handleChange}
            options={[
              { value: 15, label: '15 minutos' },
              { value: 30, label: '30 minutos' },
              { value: 45, label: '45 minutos' },
              { value: 60, label: '1 hora' },
              { value: 90, label: '1.5 horas' },
              { value: 120, label: '2 horas' },
            ]}
          />

          <FormField
            label="Precio (opcional)"
            type="number"
            name="price"
            value={formData.price}
            onChange={handleChange}
            placeholder="0.00"
            min="0"
            step="0.01"
          />
        </div>

        <FormField
          label="Notas (opcional)"
          type="textarea"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          placeholder="Información adicional sobre la cita..."
          rows={3}
        />
      </div>

      <div className="form-actions">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={loading}
        >
          Cancelar
        </Button>
        <Button
          type="submit"
          variant="primary"
          loading={loading}
        >
          {appointment ? 'Actualizar Cita' : 'Crear Cita'}
        </Button>
      </div>
    </form>
  );
};

export default AppointmentForm;

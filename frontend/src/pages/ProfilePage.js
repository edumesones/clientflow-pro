import React, { useState, useEffect, useCallback } from 'react';
import FormField from '../components/FormField';
import Button from '../components/Button';
import { professionalsAPI } from '../services/apiService';
import { useAuth } from '../context/AuthContext';
import './ProfilePage.css';

const ProfilePage = () => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    slug: '',
    specialty: '',
    bio: '',
    default_appointment_duration: 30,
    buffer_time: 0,
    booking_advance_days: 30,
    timezone: 'America/Mexico_City',
    accepting_appointments: true,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState(null);

  const fetchProfile = useCallback(async () => {
    try {
      setLoading(true);
      const response = await professionalsAPI.getMyProfile();

      if (response.data) {
        setFormData({
          full_name: response.data.full_name || '',
          email: response.data.email || '',
          phone: response.data.phone || '',
          slug: response.data.slug || '',
          specialty: response.data.specialty || '',
          bio: response.data.bio || '',
          default_appointment_duration: response.data.default_appointment_duration || 30,
          buffer_time: response.data.buffer_time || 0,
          booking_advance_days: response.data.booking_advance_days || 30,
          timezone: response.data.timezone || 'America/Mexico_City',
          accepting_appointments: response.data.accepting_appointments ?? true,
        });
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      showMessage('Error al cargar el perfil', 'error');
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.full_name.trim()) {
      newErrors.full_name = 'El nombre es requerido';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    if (formData.slug && !/^[a-z0-9-]+$/.test(formData.slug)) {
      newErrors.slug = 'El slug solo puede contener letras minúsculas, números y guiones';
    }

    if (formData.bio && formData.bio.length > 500) {
      newErrors.bio = 'La bio no puede exceder 500 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      setSaving(true);
      await professionalsAPI.updateProfile(user.id, formData);
      showMessage('Perfil actualizado exitosamente', 'success');
      await fetchProfile();
    } catch (error) {
      console.error('Error updating profile:', error);
      const errorMsg = error.response?.data?.detail || 'Error al actualizar el perfil';
      showMessage(errorMsg, 'error');
    } finally {
      setSaving(false);
    }
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 4000);
  };

  const getPublicUrl = () => {
    if (formData.slug) {
      return `${window.location.origin}/book/${formData.slug}`;
    }
    return 'Configura tu slug primero';
  };

  if (loading) {
    return <div className="profile-loading">Cargando perfil...</div>;
  }

  return (
    <div className="profile-page">
      <div className="profile-header">
        <h1>Mi Perfil Profesional</h1>
        <p className="profile-subtitle">
          Configura tu información y preferencias de negocio
        </p>
      </div>

      {message && (
        <div className={`message-banner message-${message.type}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="profile-form">
        {/* Información Básica */}
        <div className="form-section">
          <h2 className="section-title">📋 Información Básica</h2>

          <FormField
            label="Nombre completo"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            error={errors.full_name}
            required
          />

          <FormField
            label="Email"
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            error={errors.email}
            required
            disabled
            helperText="El email no se puede cambiar desde aquí"
          />

          <FormField
            label="Teléfono"
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            error={errors.phone}
            placeholder="555-123-4567"
          />
        </div>

        {/* Información Profesional */}
        <div className="form-section">
          <h2 className="section-title">💼 Información Profesional</h2>

          <FormField
            label="Slug (URL personalizada)"
            name="slug"
            value={formData.slug}
            onChange={handleChange}
            error={errors.slug}
            placeholder="tu-nombre-profesional"
            helperText="Solo letras minúsculas, números y guiones"
          />

          {formData.slug && (
            <div className="public-url-preview">
              <span className="preview-label">Tu página pública:</span>
              <a
                href={getPublicUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="preview-link"
              >
                {getPublicUrl()}
              </a>
            </div>
          )}

          <FormField
            label="Especialidad"
            name="specialty"
            value={formData.specialty}
            onChange={handleChange}
            error={errors.specialty}
            placeholder="Ej: Psicología Clínica, Fisioterapia, Coaching..."
          />

          <FormField
            label="Bio / Descripción"
            type="textarea"
            name="bio"
            value={formData.bio}
            onChange={handleChange}
            error={errors.bio}
            rows={4}
            placeholder="Cuéntale a tus clientes sobre tu experiencia y enfoque profesional..."
            helperText={`${formData.bio.length}/500 caracteres`}
          />
        </div>

        {/* Configuración de Negocio */}
        <div className="form-section">
          <h2 className="section-title">⚙️ Configuración de Negocio</h2>

          <div className="form-row">
            <FormField
              label="Duración de citas (minutos)"
              type="select"
              name="default_appointment_duration"
              value={formData.default_appointment_duration}
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
              label="Buffer entre citas (minutos)"
              type="select"
              name="buffer_time"
              value={formData.buffer_time}
              onChange={handleChange}
              options={[
                { value: 0, label: 'Sin buffer' },
                { value: 5, label: '5 minutos' },
                { value: 10, label: '10 minutos' },
                { value: 15, label: '15 minutos' },
                { value: 30, label: '30 minutos' },
              ]}
              helperText="Tiempo de descanso entre citas"
            />
          </div>

          <div className="form-row">
            <FormField
              label="Reserva anticipada (días)"
              type="number"
              name="booking_advance_days"
              value={formData.booking_advance_days}
              onChange={handleChange}
              min="7"
              max="90"
              helperText="Cuántos días adelante pueden reservar"
            />

            <FormField
              label="Zona horaria"
              type="select"
              name="timezone"
              value={formData.timezone}
              onChange={handleChange}
              options={[
                { value: 'America/Mexico_City', label: 'Ciudad de México (GMT-6)' },
                { value: 'America/Monterrey', label: 'Monterrey (GMT-6)' },
                { value: 'America/Cancun', label: 'Cancún (GMT-5)' },
                { value: 'America/Tijuana', label: 'Tijuana (GMT-8)' },
                { value: 'America/New_York', label: 'Nueva York (GMT-5)' },
                { value: 'America/Los_Angeles', label: 'Los Ángeles (GMT-8)' },
                { value: 'Europe/Madrid', label: 'Madrid (GMT+1)' },
              ]}
            />
          </div>

          <div className="accepting-toggle">
            <input
              type="checkbox"
              id="accepting_appointments"
              name="accepting_appointments"
              checked={formData.accepting_appointments}
              onChange={handleChange}
              className="toggle-checkbox"
            />
            <label htmlFor="accepting_appointments" className="toggle-label">
              <span className="toggle-text">Aceptando nuevas citas</span>
              <span className="toggle-description">
                {formData.accepting_appointments
                  ? 'Tu página pública permite reservar citas'
                  : 'Tu página pública está en modo solo consulta'}
              </span>
            </label>
          </div>
        </div>

        {/* Vista Previa */}
        <div className="form-section preview-section">
          <h2 className="section-title">👀 Vista Previa</h2>
          <div className="preview-card">
            <div className="preview-header">
              <div className="preview-avatar">
                {formData.full_name.charAt(0).toUpperCase()}
              </div>
              <div className="preview-info">
                <h3>{formData.full_name || 'Tu Nombre'}</h3>
                <p>{formData.specialty || 'Tu Especialidad'}</p>
              </div>
              {formData.accepting_appointments && (
                <span className="preview-badge">Disponible</span>
              )}
            </div>
            <p className="preview-bio">
              {formData.bio || 'Tu bio aparecerá aquí...'}
            </p>
            <div className="preview-details">
              <span>⏱️ Citas de {formData.default_appointment_duration} min</span>
              <span>📅 Reserva hasta {formData.booking_advance_days} días adelante</span>
            </div>
          </div>
        </div>

        {/* Form Actions */}
        <div className="form-actions">
          <Button
            type="button"
            variant="secondary"
            onClick={fetchProfile}
            disabled={saving}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="primary"
            loading={saving}
            disabled={saving}
          >
            Guardar Cambios
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ProfilePage;

import React, { useState, useEffect } from 'react';
import FormField from './FormField';
import Button from './Button';
import { leadsAPI } from '../services/apiService';
import './LeadForm.css';

const LeadForm = ({ lead, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    source: '',
    message: '',
    status: 'new',
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (lead) {
      setFormData({
        name: lead.name || '',
        email: lead.email || '',
        phone: lead.phone || '',
        source: lead.source || '',
        message: lead.message || '',
        status: lead.status || 'new',
      });
    }
  }, [lead]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es requerido';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'El teléfono es requerido';
    }

    if (!formData.source) {
      newErrors.source = 'La fuente es requerida';
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
      if (lead) {
        await leadsAPI.update(lead.id, formData);
      } else {
        await leadsAPI.create(formData);
      }

      onSuccess();
    } catch (error) {
      console.error('Error saving lead:', error);
      const errorMessage = error.response?.data?.detail || 'Error al guardar el lead';
      setErrors({ submit: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="lead-form">
      {errors.submit && (
        <div className="form-error-banner">
          {errors.submit}
        </div>
      )}

      <FormField
        label="Nombre completo"
        name="name"
        value={formData.name}
        onChange={handleChange}
        error={errors.name}
        required
        autoFocus
      />

      <FormField
        label="Email"
        type="email"
        name="email"
        value={formData.email}
        onChange={handleChange}
        error={errors.email}
        required
      />

      <FormField
        label="Teléfono"
        type="tel"
        name="phone"
        value={formData.phone}
        onChange={handleChange}
        error={errors.phone}
        required
        placeholder="555-123-4567"
      />

      <FormField
        label="Fuente"
        type="select"
        name="source"
        value={formData.source}
        onChange={handleChange}
        error={errors.source}
        required
        options={[
          'Web',
          'Teléfono',
          'Referido',
          'Redes Sociales',
          'Email',
          'Otro',
        ]}
      />

      <FormField
        label="Estado"
        type="select"
        name="status"
        value={formData.status}
        onChange={handleChange}
        options={[
          { value: 'new', label: 'Nuevo' },
          { value: 'contacted', label: 'Contactado' },
          { value: 'converted', label: 'Convertido' },
          { value: 'lost', label: 'Perdido' },
        ]}
      />

      <FormField
        label="Mensaje / Notas"
        type="textarea"
        name="message"
        value={formData.message}
        onChange={handleChange}
        placeholder="Mensaje del lead o notas adicionales..."
        rows={4}
      />

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
          {lead ? 'Actualizar Lead' : 'Crear Lead'}
        </Button>
      </div>
    </form>
  );
};

export default LeadForm;

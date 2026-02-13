import React, { useState, useEffect, useCallback } from 'react';
import TimeSlotPicker from '../components/TimeSlotPicker';
import Button from '../components/Button';
import { availabilityAPI } from '../services/apiService';
import './AvailabilityPage.css';

const DAYS_OF_WEEK = [
  { key: 'monday', label: 'Lunes', shortLabel: 'L' },
  { key: 'tuesday', label: 'Martes', shortLabel: 'M' },
  { key: 'wednesday', label: 'Miércoles', shortLabel: 'X' },
  { key: 'thursday', label: 'Jueves', shortLabel: 'J' },
  { key: 'friday', label: 'Viernes', shortLabel: 'V' },
  { key: 'saturday', label: 'Sábado', shortLabel: 'S' },
  { key: 'sunday', label: 'Domingo', shortLabel: 'D' },
];

const WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];

const AvailabilityPage = () => {
  const [schedule, setSchedule] = useState({
    monday: { enabled: false, slots: [] },
    tuesday: { enabled: false, slots: [] },
    wednesday: { enabled: false, slots: [] },
    thursday: { enabled: false, slots: [] },
    friday: { enabled: false, slots: [] },
    saturday: { enabled: false, slots: [] },
    sunday: { enabled: false, slots: [] },
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  const fetchSchedule = useCallback(async () => {
    try {
      setLoading(true);
      const response = await availabilityAPI.getMySlots();

      // Transform API response to schedule format
      if (response.data && Array.isArray(response.data)) {
        const transformedSchedule = { ...schedule };

        response.data.forEach(slot => {
          const dayKey = slot.day_of_week.toLowerCase();
          if (transformedSchedule[dayKey]) {
            if (!transformedSchedule[dayKey].enabled) {
              transformedSchedule[dayKey].enabled = true;
              transformedSchedule[dayKey].slots = [];
            }
            transformedSchedule[dayKey].slots.push({
              id: slot.id || Date.now() + Math.random(),
              start_time: slot.start_time,
              end_time: slot.end_time,
            });
          }
        });

        setSchedule(transformedSchedule);
      }
    } catch (error) {
      console.error('Error fetching schedule:', error);
      showMessage('Error al cargar el horario', 'error');
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchSchedule();
  }, [fetchSchedule]);

  const toggleDay = (dayKey) => {
    setSchedule(prev => ({
      ...prev,
      [dayKey]: {
        ...prev[dayKey],
        enabled: !prev[dayKey].enabled,
        slots: prev[dayKey].enabled ? [] : prev[dayKey].slots,
      },
    }));
  };

  const updateDaySlots = (dayKey, slots) => {
    setSchedule(prev => ({
      ...prev,
      [dayKey]: {
        ...prev[dayKey],
        slots,
      },
    }));
  };

  const copyToWeekdays = () => {
    // Find the first enabled day to use as template
    const templateDay = WEEKDAYS.find(day => schedule[day].enabled && schedule[day].slots.length > 0);

    if (!templateDay) {
      showMessage('Configura al menos un día laboral primero', 'error');
      return;
    }

    const templateSlots = schedule[templateDay].slots.map(slot => ({
      ...slot,
      id: Date.now() + Math.random(), // Generate new IDs
    }));

    const updatedSchedule = { ...schedule };
    WEEKDAYS.forEach(day => {
      updatedSchedule[day] = {
        enabled: true,
        slots: templateSlots.map(slot => ({
          ...slot,
          id: Date.now() + Math.random(),
        })),
      };
    });

    setSchedule(updatedSchedule);
    showMessage('Horario copiado a días laborales (L-V)', 'success');
  };

  const clearAll = () => {
    if (window.confirm('¿Estás seguro de que deseas limpiar todo el horario?')) {
      const clearedSchedule = {};
      Object.keys(schedule).forEach(day => {
        clearedSchedule[day] = { enabled: false, slots: [] };
      });
      setSchedule(clearedSchedule);
      showMessage('Horario limpiado', 'success');
    }
  };

  const calculateTotalSlots = () => {
    let total = 0;
    Object.values(schedule).forEach(day => {
      if (day.enabled) {
        day.slots.forEach(slot => {
          const [startHour, startMin] = slot.start_time.split(':').map(Number);
          const [endHour, endMin] = slot.end_time.split(':').map(Number);
          const durationMinutes = (endHour * 60 + endMin) - (startHour * 60 + startMin);
          // Assuming 30-minute appointment slots
          total += Math.floor(durationMinutes / 30);
        });
      }
    });
    return total;
  };

  const handleSave = async () => {
    try {
      setSaving(true);

      // Transform schedule to API format
      const scheduleData = [];
      Object.entries(schedule).forEach(([dayKey, dayData]) => {
        if (dayData.enabled && dayData.slots.length > 0) {
          dayData.slots.forEach(slot => {
            scheduleData.push({
              day_of_week: dayKey.charAt(0).toUpperCase() + dayKey.slice(1),
              start_time: slot.start_time,
              end_time: slot.end_time,
            });
          });
        }
      });

      if (scheduleData.length === 0) {
        showMessage('Configura al menos un horario antes de guardar', 'error');
        return;
      }

      await availabilityAPI.setSchedule({ slots: scheduleData });
      showMessage('Horario guardado exitosamente', 'success');
      await fetchSchedule(); // Refresh to get IDs from backend
    } catch (error) {
      console.error('Error saving schedule:', error);
      const errorMsg = error.response?.data?.detail || 'Error al guardar el horario';
      showMessage(errorMsg, 'error');
    } finally {
      setSaving(false);
    }
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 4000);
  };

  if (loading) {
    return <div className="availability-loading">Cargando horario...</div>;
  }

  const totalSlots = calculateTotalSlots();

  return (
    <div className="availability-page">
      <div className="availability-header">
        <div>
          <h1>Configurar Disponibilidad</h1>
          <p className="availability-subtitle">
            Define tu horario semanal de atención
          </p>
        </div>
        <div className="header-actions">
          <Button variant="secondary" onClick={copyToWeekdays}>
            Copiar a L-V
          </Button>
          <Button variant="danger" onClick={clearAll}>
            Limpiar Todo
          </Button>
        </div>
      </div>

      {message && (
        <div className={`message-banner message-${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="schedule-grid">
        {DAYS_OF_WEEK.map(day => (
          <div key={day.key} className="day-card">
            <div className="day-header">
              <div className="day-toggle">
                <input
                  type="checkbox"
                  id={`toggle-${day.key}`}
                  checked={schedule[day.key].enabled}
                  onChange={() => toggleDay(day.key)}
                  className="day-checkbox"
                />
                <label htmlFor={`toggle-${day.key}`} className="day-label">
                  <span className="day-name">{day.label}</span>
                  <span className="day-short">{day.shortLabel}</span>
                </label>
              </div>
              {schedule[day.key].enabled && (
                <span className="slot-count">
                  {schedule[day.key].slots.length} {schedule[day.key].slots.length === 1 ? 'horario' : 'horarios'}
                </span>
              )}
            </div>

            {schedule[day.key].enabled && (
              <div className="day-slots">
                <TimeSlotPicker
                  slots={schedule[day.key].slots}
                  onSlotsChange={(slots) => updateDaySlots(day.key, slots)}
                  dayName={day.label}
                />
              </div>
            )}

            {!schedule[day.key].enabled && (
              <p className="day-disabled">Día inactivo</p>
            )}
          </div>
        ))}
      </div>

      <div className="availability-footer">
        <div className="footer-info">
          <div className="info-item">
            <span className="info-icon">📊</span>
            <div className="info-text">
              <span className="info-label">Slots disponibles</span>
              <span className="info-value">{totalSlots} por semana</span>
            </div>
          </div>
          <div className="info-item">
            <span className="info-icon">📅</span>
            <div className="info-text">
              <span className="info-label">Días activos</span>
              <span className="info-value">
                {Object.values(schedule).filter(d => d.enabled).length} de 7
              </span>
            </div>
          </div>
        </div>

        <Button
          variant="primary"
          size="large"
          onClick={handleSave}
          loading={saving}
          disabled={saving}
        >
          Guardar Horario
        </Button>
      </div>
    </div>
  );
};

export default AvailabilityPage;

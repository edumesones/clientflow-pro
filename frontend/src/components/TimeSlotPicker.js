import React, { useState, useEffect } from 'react';
import Button from './Button';
import './TimeSlotPicker.css';

const TimeSlotPicker = ({ slots, onSlotsChange, dayName }) => {
  const [localSlots, setLocalSlots] = useState(slots || []);

  useEffect(() => {
    setLocalSlots(slots || []);
  }, [slots]);

  const generateTimeOptions = () => {
    const options = [];
    for (let hour = 0; hour < 24; hour++) {
      for (let minute = 0; minute < 60; minute += 15) {
        const timeString = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
        options.push(timeString);
      }
    }
    return options;
  };

  const timeOptions = generateTimeOptions();

  const addSlot = () => {
    const newSlot = {
      id: Date.now(),
      start_time: '09:00',
      end_time: '17:00',
    };
    const updatedSlots = [...localSlots, newSlot];
    setLocalSlots(updatedSlots);
    onSlotsChange(updatedSlots);
  };

  const removeSlot = (slotId) => {
    const updatedSlots = localSlots.filter(slot => slot.id !== slotId);
    setLocalSlots(updatedSlots);
    onSlotsChange(updatedSlots);
  };

  const updateSlot = (slotId, field, value) => {
    const updatedSlots = localSlots.map(slot => {
      if (slot.id === slotId) {
        const updated = { ...slot, [field]: value };

        // Validate that end_time is after start_time
        if (field === 'start_time' && updated.end_time <= value) {
          // Auto-adjust end time to be 1 hour after start
          const [hours, minutes] = value.split(':').map(Number);
          const endHour = (hours + 1) % 24;
          updated.end_time = `${String(endHour).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
        }

        if (field === 'end_time' && value <= updated.start_time) {
          // Don't update if end time would be before or equal to start time
          return slot;
        }

        return updated;
      }
      return slot;
    });

    setLocalSlots(updatedSlots);
    onSlotsChange(updatedSlots);
  };

  const checkOverlap = (slotId, startTime, endTime) => {
    return localSlots.some(slot => {
      if (slot.id === slotId) return false;

      const slotStart = slot.start_time;
      const slotEnd = slot.end_time;

      // Check if slots overlap
      return (
        (startTime >= slotStart && startTime < slotEnd) ||
        (endTime > slotStart && endTime <= slotEnd) ||
        (startTime <= slotStart && endTime >= slotEnd)
      );
    });
  };

  return (
    <div className="time-slot-picker">
      <div className="slots-container">
        {localSlots.length === 0 ? (
          <p className="no-slots">No hay horarios configurados para {dayName}</p>
        ) : (
          localSlots.map((slot) => {
            const hasOverlap = checkOverlap(slot.id, slot.start_time, slot.end_time);

            return (
              <div key={slot.id} className={`slot-row ${hasOverlap ? 'slot-overlap' : ''}`}>
                <div className="slot-inputs">
                  <div className="time-input-group">
                    <label>Desde:</label>
                    <select
                      value={slot.start_time}
                      onChange={(e) => updateSlot(slot.id, 'start_time', e.target.value)}
                      className="time-select"
                    >
                      {timeOptions.map(time => (
                        <option key={time} value={time}>{time}</option>
                      ))}
                    </select>
                  </div>

                  <span className="time-separator">—</span>

                  <div className="time-input-group">
                    <label>Hasta:</label>
                    <select
                      value={slot.end_time}
                      onChange={(e) => updateSlot(slot.id, 'end_time', e.target.value)}
                      className="time-select"
                    >
                      {timeOptions.map(time => (
                        <option key={time} value={time}>{time}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <Button
                  variant="danger"
                  size="small"
                  onClick={() => removeSlot(slot.id)}
                  aria-label="Eliminar horario"
                >
                  ✕
                </Button>

                {hasOverlap && (
                  <span className="overlap-warning">⚠️ Solapamiento detectado</span>
                )}
              </div>
            );
          })
        )}
      </div>

      <Button
        variant="ghost"
        size="small"
        onClick={addSlot}
        className="add-slot-btn"
      >
        + Agregar horario
      </Button>
    </div>
  );
};

export default TimeSlotPicker;

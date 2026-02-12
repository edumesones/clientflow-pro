import React from 'react';
import './FormField.css';

const FormField = ({
  label,
  type = 'text',
  name,
  value,
  onChange,
  error,
  required = false,
  placeholder,
  disabled = false,
  options = [], // For select type
  rows = 4, // For textarea
  min,
  max,
  step,
  pattern,
  autoFocus = false,
}) => {
  const fieldId = `field-${name}`;

  const renderInput = () => {
    const commonProps = {
      id: fieldId,
      name,
      value: value || '',
      onChange,
      required,
      disabled,
      placeholder,
      className: `form-input ${error ? 'error' : ''}`,
      autoFocus,
    };

    switch (type) {
      case 'textarea':
        return <textarea {...commonProps} rows={rows} />;

      case 'select':
        return (
          <select {...commonProps}>
            <option value="">Seleccionar...</option>
            {options.map((option) => (
              <option
                key={typeof option === 'string' ? option : option.value}
                value={typeof option === 'string' ? option : option.value}
              >
                {typeof option === 'string' ? option : option.label}
              </option>
            ))}
          </select>
        );

      case 'date':
      case 'time':
      case 'datetime-local':
        return (
          <input
            {...commonProps}
            type={type}
            min={min}
            max={max}
          />
        );

      case 'number':
        return (
          <input
            {...commonProps}
            type="number"
            min={min}
            max={max}
            step={step}
          />
        );

      case 'email':
        return (
          <input
            {...commonProps}
            type="email"
            pattern={pattern}
          />
        );

      case 'tel':
      case 'phone':
        return (
          <input
            {...commonProps}
            type="tel"
            pattern={pattern || '[0-9]{3}-[0-9]{3}-[0-9]{4}'}
            placeholder={placeholder || '555-123-4567'}
          />
        );

      case 'password':
        return (
          <input
            {...commonProps}
            type="password"
            minLength={min}
            maxLength={max}
          />
        );

      default:
        return (
          <input
            {...commonProps}
            type={type}
            pattern={pattern}
            minLength={min}
            maxLength={max}
          />
        );
    }
  };

  return (
    <div className="form-field">
      {label && (
        <label htmlFor={fieldId} className="form-label">
          {label}
          {required && <span className="required-asterisk">*</span>}
        </label>
      )}

      {renderInput()}

      {error && (
        <div className="form-error">
          <span className="error-icon">⚠️</span>
          <span className="error-text">{error}</span>
        </div>
      )}
    </div>
  );
};

export default FormField;

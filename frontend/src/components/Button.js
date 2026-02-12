import React from 'react';
import './Button.css';

const Button = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary', // primary, secondary, danger, success, ghost
  size = 'medium', // small, medium, large
  disabled = false,
  loading = false,
  fullWidth = false,
  icon,
  className = '',
}) => {
  const buttonClasses = [
    'btn',
    `btn-${variant}`,
    `btn-${size}`,
    fullWidth && 'btn-fullwidth',
    loading && 'btn-loading',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading && (
        <span className="btn-spinner"></span>
      )}

      {!loading && icon && (
        <span className="btn-icon">{icon}</span>
      )}

      <span className="btn-text">{children}</span>
    </button>
  );
};

export default Button;

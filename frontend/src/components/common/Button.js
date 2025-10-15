import React from 'react';
import '../../styles/components/button.css';

const Button = ({ 
  children, 
  type = 'button', 
  variant = 'primary', 
  onClick, 
  disabled = false,
  fullWidth = false 
}) => {
  const classNames = [
    'btn',
    `btn--${variant}`,
    fullWidth ? 'btn--full-width' : '',
    disabled ? 'btn--disabled' : ''
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      className={classNames}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default Button;
import React from 'react';
import '../../styles/components/input.css';

const Input = ({
  type = 'text',
  name,
  value,
  onChange,
  placeholder,
  label,
  error,
  required = false
}) => {
  return (
    <div className="input-group">
      {label && (
        <label htmlFor={name} className="input-group__label">
          {label}
          {required && <span className="input-group__required">*</span>}
        </label>
      )}
      <input
        type={type}
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`input-group__input ${error ? 'input-group__input--error' : ''}`}
        required={required}
      />
      {error && <span className="input-group__error">{error}</span>}
    </div>
  );
};

export default Input;
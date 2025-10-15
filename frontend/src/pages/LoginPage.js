import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import '../styles/pages/login.css';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, error: authError } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.username.trim()) {
      newErrors.username = 'Le nom d\'utilisateur est requis';
    }
    if (!formData.password) {
      newErrors.password = 'Le mot de passe est requis';
    }
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    const result = await login(formData.username, formData.password);
    setLoading(false);

    if (result.success) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="login-page">
      <div className="login-page__container">
        <div className="login-page__header">
          <h1 className="login-page__title">ShareTech</h1>
          <p className="login-page__subtitle">Connectez-vous à votre compte</p>
        </div>

        <form className="login-page__form" onSubmit={handleSubmit}>
          <Input
            type="text"
            name="username"
            label="Identifiant"
            value={formData.username}
            onChange={handleChange}
            placeholder="Votre nom d'utilisateur"
            error={errors.username}
            required
          />

          <Input
            type="password"
            name="password"
            label="Mot de passe"
            value={formData.password}
            onChange={handleChange}
            placeholder="Votre mot de passe"
            error={errors.password}
            required
          />

          {authError && (
            <div className="login-page__error">
              {authError}
            </div>
          )}

          <Button
            type="submit"
            variant="primary"
            fullWidth
            disabled={loading}
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </Button>
        </form>

        <div className="login-page__footer">
          <p className="text-sm text-muted">
            Si problème de connexion, contactez l'IT
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
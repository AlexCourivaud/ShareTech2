import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/common/Button';

const DashboardPage = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    window.location.href = '/';
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Dashboard</h1>
      <p>Bienvenue, {user?.username} !</p>
      <p>Rôle : {user?.profile?.role}</p>
      <Button onClick={handleLogout} variant="danger">
        Se déconnecter
      </Button>
      <p style={{ marginTop: '2rem', color: '#666' }}>
        Page de Dashboard !
      </p>
    </div>
  );
};

export default DashboardPage;
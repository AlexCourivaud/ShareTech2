import api from './apiConfig';

const authService = {
  // Connexion
  login: async (username, password) => {
    try {
      const response = await api.post('/api/accounts/login/', {
        username,
        password,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Erreur de connexion' };
    }
  },

  // Déconnexion
  logout: async () => {
    try {
      const response = await api.post('/api/accounts/logout/');
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Erreur de déconnexion' };
    }
  },

  // Récupérer le profil de l'utilisateur connecté
  getProfile: async () => {
    try {
      const response = await api.get('/api/accounts/profile/');
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Erreur de récupération du profil' };
    }
  },

  // Inscription (si besoin plus tard)
  register: async (userData) => {
    try {
      const response = await api.post('/api/accounts/register/', userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Erreur lors de l\'inscription' };
    }
  },
};

export default authService;
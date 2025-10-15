import api from './apiConfig';

const projectService = {
  getAll: async () => {
    const response = await api.get('/api/projects/');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/api/projects/${id}/`);
    return response.data;
  },

  getMembers: async (id) => {
    const response = await api.get(`/api/projects/${id}/members/`);
    return response.data;
  }
};

export default projectService;
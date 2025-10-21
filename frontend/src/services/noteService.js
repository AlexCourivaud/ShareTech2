import api from './apiConfig';

const noteService = {
  getAll: async () => {
    const response = await api.get('/api/notes/');
    return response.data;
  },

  getByProject: async (projectId) => {
    const response = await api.get(`/api/notes/?project=${projectId}`);
    return response.data;
  }
};

export default noteService;
import api from './apiConfig';

const taskService = {
  getAll: async () => {
    const response = await api.get('/api/tasks/');
    return response.data;
  },

  getMyTasks: async () => {

    const response = await api.get('/api/tasks/');
    return response.data;
  }
};

export default taskService;
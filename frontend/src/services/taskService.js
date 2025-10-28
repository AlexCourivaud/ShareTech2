import api from "./apiConfig";

const taskService = {
  /**
   * Récupérer toutes les tâches accessibles
   */
  getAll: async () => {
    const response = await api.get("/api/tasks/");
    return response.data;
  },

  /**
   * Récupérer les tâches d'un projet
   */
  getByProject: async (projectId) => {
    const response = await api.get(`/api/tasks/?project=${projectId}`);
    return response.data;
  },

  /**
   * Récupérer mes tâches assignées
   */
  getMyTasks: async () => {
    const response = await api.get("/api/tasks/my_tasks/");
    return response.data;
  },

  /**
   * Récupérer une tâche par ID
   */
  getById: async (taskId) => {
    const response = await api.get(`/api/tasks/${taskId}/`);
    return response.data;
  },

  /**
   * Créer une nouvelle tâche
   */
  create: async (taskData) => {
    const response = await api.post("/api/tasks/", taskData);
    return response.data;
  },

  /**
   * Mettre à jour une tâche
   */
  update: async (taskId, taskData) => {
    const response = await api.put(`/api/tasks/${taskId}/`, taskData);
    return response.data;
  },

  /**
   * Supprimer une tâche
   */
  delete: async (taskId) => {
    const response = await api.delete(`/api/tasks/${taskId}/`);
    return response.data;
  },

  /**
   * Assigner une tâche à un utilisateur
   */
  assign: async (taskId, userId) => {
    const response = await api.post(`/api/tasks/${taskId}/assign/`, {
      user_id: userId,
    });
    return response.data;
  },

  /**
   * Retirer l'assignation d'une tâche
   */
  unassign: async (taskId) => {
    const response = await api.post(`/api/tasks/${taskId}/unassign/`);
    return response.data;
  },

  /**
   * Changer le statut d'une tâche
   */
  changeStatus: async (taskId, status) => {
    const response = await api.post(`/api/tasks/${taskId}/change_status/`, {
      status: status,
    });
    return response.data;
  },
};

export default taskService;
import api from "./apiConfig";

const noteService = {
  getAll: async () => {
    const response = await api.get("/api/notes/");
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/api/notes/${id}/`);
    return response.data;
  },

  getByProject: async (projectId) => {
    const response = await api.get(`api/notes/?project=${projectId}`);
    return response.data;
  },

  createNote: async (projectId, data) => {
    const response = await api.post("/api/notes/", {
      ...data,
      project: projectId,
    });
    return response.data;
  },

  updateNote: async (noteId, data) => {
    const response = await api.put(`/api/notes/${noteId}/`, data);
    return response.data;
  },

  deleteNote: async (noteId) => {
    await api.delete(`/api/notes/${noteId}/`);
  },
};

export default noteService;

import apiConfig from "./apiConfig";

const commentService = {
  getCommentsByNote: async (noteId) => {
    const response = await apiConfig.get(`/api/notes/${noteId}/comments/`);
    return response.data;
  },

  createComment: async (noteId, content) => {
    const response = await apiConfig.post(`/api/notes/${noteId}/comments/`, {
      content,
    });
    return response.data;
  },

  replyToComment: async (commentId, content) => {
    const response = await apiConfig.post(`/api/comments/${commentId}/replies/`, {
      content,
    });
    return response.data;
  },

  updateComment: async (commentId, content) => {
    const response = await apiConfig.put(`/api/comments/${commentId}/`, {
      content,
    });
    return response.data;
  },

  deleteComment: async (commentId) => {
    await apiConfig.delete(`/api/comments/${commentId}/`);
  },
};

export default commentService;

const API_BASE_URL = "http://localhost:8000/api";

class ApiService {
  async fetchProjects() {
    try {
      const response = await fetch(`${API_BASE_URL}/projects/`);
      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error("Erreur lors du chargement des projets:", error);
      return [];
    }
  }

  async fetchNotes() {
    try {
      const response = await fetch(`${API_BASE_URL}/notes/`);
      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error("Erreur lors du chargement des notes:", error);
      return [];
    }
  }
}

export default new ApiService();

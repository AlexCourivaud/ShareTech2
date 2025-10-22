import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import Navbar from "../components/layout/Navbar";
import projectService from "../services/projectService";
import taskService from "../services/taskService";
import "../styles/pages/dashboard.css";

const DashboardPage = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setError(null);

      // Charger projets
      const projectsData = await projectService.getAll();
      setProjects(projectsData);

      // Charger tâches (avec gestion d'erreur)
      try {
        const tasksData = await taskService.getMyTasks();
        setTasks(tasksData);
      } catch (taskError) {
        console.warn("Impossible de charger les tâches:", taskError);
        setTasks([]);
      }
    } catch (error) {
      console.error("Erreur chargement données:", error);
      setError("Impossible de charger les données");
    } finally {
      setLoading(false);
    }
  };

  if (loading)
    return (
      <div className="dashboard-page">
        <Navbar />
        <div className="dashboard-page__container">
          <p>Chargement...</p>
        </div>
      </div>
    );

  if (error)
    return (
      <div className="dashboard-page">
        <Navbar />
        <div className="dashboard-page__container">
          <p style={{ color: "red" }}>{error}</p>
        </div>
      </div>
    );

  return (
    <div className="dashboard-page">
      <Navbar />

      <div className="dashboard-page__container">
        <h1>Bienvenue, {user?.username} !</h1>

        <div className="dashboard-page__grid">
          {/* Colonne 1 : Favoris */}
          <div className="dashboard-page__column">
            <h2>Vos Favoris</h2>
            <div className="dashboard-page__card">
              <p className="text-muted">Aucun favori</p>
            </div>
          </div>

          {/* Colonne 2 : Tâches */}
          <div className="dashboard-page__column">
            <h2>Vos Tâches ({tasks.length})</h2>
            <div className="dashboard-page__card">
              {tasks.length > 0 ? (
                tasks.map((task) => (
                  <div key={task.id} className="task-item">
                    <h4>{task.title}</h4>
                    <span className={`badge badge--${task.status}`}>
                      {task.status}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-muted">Aucune tâche</p>
              )}
            </div>
          </div>

          {/* Colonne 3 : Projets */}
          <div className="dashboard-page__column">
            <h2>Vos Projets ({projects.length})</h2>
            <div className="dashboard-page__card">
              {projects.length > 0 ? (
                projects.map((project) => (
                  <Link
                    key={project.id}
                    to={`/projects/${project.id}`}
                    className="project-item"
                  >
                    <h4>{project.name}</h4>
                    <p className="text-muted text-sm">{project.description}</p>
                  </Link>
                ))
              ) : (
                <p className="text-muted">Aucun projet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;

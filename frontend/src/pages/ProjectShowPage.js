import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Navbar from "../components/layout/Navbar";
import projectService from "../services/projectService";
import noteService from "../services/noteService";
import taskService from "../services/taskService";
import "../styles/pages/project-show.css";

const ProjectShowPage = () => {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [notes, setNotes] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setError(null);

      const projectData = await projectService.getById(id);
      setProject(projectData);

      try {
        const notesData = await noteService.getByProject(id);
        setNotes(notesData);
      } catch (e) {
        console.warn("Impossible de charger les notes");
        setNotes([]);
      }

      try {
        const tasksData = await taskService.getByProject(id);
        setTasks(tasksData);
      } catch (e) {
        console.warn("Impossible de charger les tâches");
        setTasks([]);
      }

      try {
        const membersData = await projectService.getMembers(id);
        setMembers(membersData);
      } catch (e) {
        console.warn("Impossible de charger les membres");
        setMembers([]);
      }
    } catch (error) {
      console.error("Erreur:", error);
      setError("Projet introuvable");
    } finally {
      setLoading(false);
    }
  };

  if (loading)
    return (
      <div className="project-show-page">
        <Navbar />
        <div className="project-show-page__loading">
          <p>Chargement...</p>
        </div>
      </div>
    );

  if (error || !project)
    return (
      <div className="project-show-page">
        <Navbar />
        <div className="project-show-page__error">
          <p>{error || "Projet introuvable"}</p>
        </div>
      </div>
    );

  return (
    <div className="project-show-page">
      <Navbar />

      <div className="project-show-page__layout">
        {/* COLONNE GAUCHE : Notes */}
        <div className="project-show-page__left">
          <div className="project-show-page__section">
            <h2>Notes du projet ({notes.length})</h2>
            <div className="project-show-page__notes-list">
              {notes.length > 0 ? (
                notes.map((note) => (
                  <div key={note.id} className="note-card">
                    <h4>{note.title}</h4>
                    <p className="note-excerpt">
                      {note.excerpt || note.content?.substring(0, 150)}...
                    </p>
                  </div>
                ))
              ) : (
                <p className="empty-message">Aucune note</p>
              )}
            </div>
          </div>
        </div>

        {/* COLONNE DROITE */}
        <div className="project-show-page__right">
          {/* HAUT : Infos projet */}
          <div className="project-show-page__project-info">
            {/* Image projet */}
            <div className="project-image-placeholder">
              <span className="image-icon">📷</span>
            </div>

            {/* Détails projet */}
            <div className="project-details">
              <h1>{project.name}</h1>
              <p className="project-description">{project.description}</p>
            </div>

            {/* Participants */}
            <div className="project-members">
              <h3>👥 Participants ({members.length})</h3>
              <div className="members-list">
                {members.length > 0 ? (
                  members.map((member) => {
                    // Vérification de sécurité
                    const username =
                      member.user?.username || member.username || "Utilisateur";
                    const initial = username.charAt(0).toUpperCase();

                    return (
                      <div key={member.id} className="member-item">
                        <div className="member-avatar">{initial}</div>
                        <span className="member-name">{username}</span>
                      </div>
                    );
                  })
                ) : (
                  <p className="empty-message">Aucun participant</p>
                )}
              </div>
            </div>
          </div>

          {/* BAS : Tâches */}
          <div className="project-show-page__tasks">
            <h2>Tâches du projet ({tasks.length})</h2>
            <div className="tasks-list">
              {tasks.length > 0 ? (
                tasks.map((task) => (
                  <div key={task.id} className="task-card">
                    <h4>{task.title}</h4>
                    <p className="task-description">
                      {task.description || "Pas de description"}
                    </p>
                    <div className="task-badges">
                      <span
                        className={`badge badge-status status-${task.status}`}
                      >
                        {task.status}
                      </span>
                      <span
                        className={`badge badge-priority priority-${task.priority}`}
                      >
                        {task.priority}
                      </span>
                      {task.assigned_to ? (
                        <span className="badge badge-assigned">
                          👤 {task.assigned_to.username}
                        </span>
                      ) : (
                        <span className="badge badge-unassigned">
                          Non assignée
                        </span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <p className="empty-message">Aucune tâche</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectShowPage;

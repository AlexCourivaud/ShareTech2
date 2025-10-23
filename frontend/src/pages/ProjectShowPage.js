import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Navbar from "../components/layout/Navbar";
import projectService from "../services/projectService";
import noteService from "../services/noteService";
import taskService from "../services/taskService";
import commentService from "../services/commentService";
import CommentSection from "../components/comments/CommentSection";
import "../styles/pages/project-show.css";

const ProjectShowPage = () => {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [notes, setNotes] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [members, setMembers] = useState([]);
  const [expandedNoteId, setExpandedNoteId] = useState(null);
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
        console.log(" NOTES DATA:", notesData); // TODO test
        const notesWithComments = await Promise.all(
          notesData.map(async (note) => {
            console.log("UNE NOTE:", note); // TODO test2
            try {
              const comments = await commentService.getCommentsByNote(note.id);
              return { ...note, commentsCount: comments.length };
            } catch {
              return { ...note, commentsCount: 0 };
            }
          })
        );

        setNotes(notesWithComments);
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

  const toggleNote = (noteId) => {
    setExpandedNoteId(expandedNoteId === noteId ? null : noteId);
  };

  if (loading) {
    return (
      <div className="project-show-page">
        <Navbar />
        <div className="project-show-page__loading">
          <p>Chargement...</p>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="project-show-page">
        <Navbar />
        <div className="project-show-page__error">
          <p>{error || "Projet introuvable"}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="project-show-page">
      <Navbar />

      <div className="project-show-page__layout">
        <div className="project-show-page__left">
          <div className="project-show-page__section">
            <h2>Notes du projet ({notes.length})</h2>
            <div className="project-show-page__notes-list">
              {notes.length > 0 ? (
                notes.map((note) => (
                  <div key={note.id} className="note-card">
                    <div
                      className="note-card__header"
                      onClick={() => toggleNote(note.id)}
                    >
                      <h4>{note.title}</h4>
                      <p className="note-excerpt">{note.content}</p>
                      <small className="note-meta">
                        👤 {note.author_username} | Crée le 📅{" "}
                        {new Date(note.created_at).toLocaleDateString()} | 💬{" "}
                        {note.commentsCount || 0} commentaire
                        {note.commentsCount !== 1 ? "s" : ""}
                      </small>
                    </div>

                    {expandedNoteId === note.id && (
                      <div className="note-card__expanded">
                        <div className="note-content">{note.content}</div>
                        <CommentSection noteId={note.id} />
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p className="empty-message">Aucune note</p>
              )}
            </div>
          </div>
        </div>

        <div className="project-show-page__right">
          <div className="project-show-page__project-info">
            <div className="project-image-placeholder">
              <span className="image-icon">photo du projet</span>
            </div>

            <div className="project-details">
              <h1>{project.name}</h1>
              <p className="project-description">{project.description}</p>
            </div>

            <div className="project-members">
              <h3>👥 Participants ({members.length})</h3>
              <div className="members-list">
                {members.length > 0 ? (
                  members.map((member) => {
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

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
  const [editingNoteId, setEditingNoteId] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // États pour les formulaires
  const [createFormData, setCreateFormData] = useState({
    title: "",
    content: "",
  });
  const [editFormData, setEditFormData] = useState({ title: "", content: "" });

  // Utilisateur connecté (récupéré du contexte normalement, ici simplifié)
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    loadData();
    loadCurrentUser();
  }, [id]);

  const loadCurrentUser = async () => {
    try {
      // Simule la récupération du user depuis AuthContext ou API
      // Pour l'instant, on va checker directement via l'API profile
      const response = await fetch(
        "http://localhost:8000/api/accounts/profile/",
        {
          credentials: "include",
        }
      );
      if (response.ok) {
        const userData = await response.json();
        setCurrentUser(userData);
      }
    } catch (e) {
      console.warn("Impossible de charger l'utilisateur");
    }
  };

  const loadData = async () => {
    try {
      setError(null);

      const projectData = await projectService.getById(id);
      setProject(projectData);

      try {
        const notesData = await noteService.getByProject(id);

        const notesWithComments = await Promise.all(
          notesData.map(async (note) => {
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
    setEditingNoteId(null); // Ferme le mode édition si ouvert
  };

  // Vérifier si l'utilisateur peut modifier/supprimer une note
  const canEditNote = (note) => {
    if (!currentUser) return false;
    return (
      note.author_username === currentUser.username ||
      currentUser.profile?.role === "admin"
    );
  };

  // CRÉATION
  const handleCreateNote = async (e) => {
    e.preventDefault();

    if (!createFormData.title.trim() || !createFormData.content.trim()) {
      alert("Titre et contenu requis");
      return;
    }

    try {
      await noteService.createNote(id, createFormData);
      setCreateFormData({ title: "", content: "" });
      setShowCreateForm(false);
      loadData(); // Recharger les notes
    } catch (error) {
      console.error("Erreur création note:", error);
      alert("Erreur lors de la création de la note");
    }
  };

  // MODIFICATION
  const startEditNote = (note) => {
    setEditingNoteId(note.id);
    setEditFormData({ title: note.title, content: note.content });
  };

  const handleUpdateNote = async (noteId) => {
    if (!editFormData.title.trim() || !editFormData.content.trim()) {
      alert("Titre et contenu requis");
      return;
    }

    try {
      await noteService.updateNote(noteId, editFormData);
      setEditingNoteId(null);
      loadData(); // Recharger les notes
    } catch (error) {
      console.error("Erreur modification note:", error);
      alert("Erreur lors de la modification de la note");
    }
  };

  // SUPPRESSION
  const handleDeleteNote = async (noteId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer cette note ?")) {
      return;
    }

    try {
      await noteService.deleteNote(noteId);
      loadData(); // Recharger les notes
    } catch (error) {
      console.error("Erreur suppression note:", error);
      alert("Erreur lors de la suppression de la note");
    }
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
            <div className="notes-header">
              <h2>Notes du projet ({notes.length})</h2>
              <button
                className="btn-create-note"
                onClick={() => setShowCreateForm(!showCreateForm)}
              >
                {showCreateForm ? "Annuler" : "+ Nouvelle note"}
              </button>
            </div>

            {/* FORMULAIRE CRÉATION */}
            {showCreateForm && (
              <form onSubmit={handleCreateNote} className="note-form">
                <input
                  type="text"
                  placeholder="Titre de la note"
                  value={createFormData.title}
                  onChange={(e) =>
                    setCreateFormData({
                      ...createFormData,
                      title: e.target.value,
                    })
                  }
                  className="note-form-input"
                />
                <textarea
                  placeholder="Contenu de la note"
                  value={createFormData.content}
                  onChange={(e) =>
                    setCreateFormData({
                      ...createFormData,
                      content: e.target.value,
                    })
                  }
                  className="note-form-textarea"
                  rows="6"
                />
                <div className="note-form-actions">
                  <button type="submit" className="btn-save">
                    Enregistrer
                  </button>
                  <button
                    type="button"
                    className="btn-cancel"
                    onClick={() => {
                      setShowCreateForm(false);
                      setCreateFormData({ title: "", content: "" });
                    }}
                  >
                    Annuler
                  </button>
                </div>
              </form>
            )}

            {/* LISTE DES NOTES */}
            <div className="project-show-page__notes-list">
              {notes.length > 0 ? (
                notes.map((note) => (
                  <div key={note.id} className="note-card">
                    {editingNoteId === note.id ? (
                      // MODE ÉDITION
                      <div className="note-edit-form">
                        <input
                          type="text"
                          value={editFormData.title}
                          onChange={(e) =>
                            setEditFormData({
                              ...editFormData,
                              title: e.target.value,
                            })
                          }
                          className="note-form-input"
                        />
                        <textarea
                          value={editFormData.content}
                          onChange={(e) =>
                            setEditFormData({
                              ...editFormData,
                              content: e.target.value,
                            })
                          }
                          className="note-form-textarea"
                          rows="8"
                        />
                        <div className="note-form-actions">
                          <button
                            className="btn-save"
                            onClick={() => handleUpdateNote(note.id)}
                          >
                            Enregistrer
                          </button>
                          <button
                            className="btn-cancel"
                            onClick={() => setEditingNoteId(null)}
                          >
                            Annuler
                          </button>
                        </div>
                      </div>
                    ) : (
                      // MODE AFFICHAGE
                      <>
                        <div
                          className="note-card__header"
                          onClick={() => toggleNote(note.id)}
                        >
                          <h4>{note.title}</h4>
                          <p className="note-excerpt">
                            {note.content?.substring(0, 150)}
                            {note.content?.length > 150 ? "..." : ""}
                          </p>
                          <small className="note-meta">
                            {note.author_username} | {" "}
                            {new Date(note.created_at).toLocaleDateString()} |
                             {note.commentsCount || 0} commentaire
                            {note.commentsCount !== 1 ? "s" : ""}
                          </small>
                        </div>

                        {expandedNoteId === note.id && (
                          <div className="note-card__expanded">
                            <div className="note-content-header">
                              <h3>{note.title}</h3>
                              {canEditNote(note) && (
                                <div className="note-actions">
                                  <button
                                    className="btn-edit"
                                    onClick={() => startEditNote(note)}
                                  >
                                    Modifier
                                  </button>
                                  <button
                                    className="btn-delete"
                                    onClick={() => handleDeleteNote(note.id)}
                                  >
                                    Supprimer
                                  </button>
                                </div>
                              )}
                            </div>
                            <div className="note-content">{note.content}</div>
                            <CommentSection noteId={note.id} />
                          </div>
                        )}
                      </>
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
            <div className="project-details">
              <h1>{project.name}</h1>
              <p className="project-description">{project.description}</p>
            </div>

            <div className="project-image-placeholder">
              <span className="image-icon"></span>
            </div>

            <div className="project-members">
              <h3>Participants ({members.length})</h3>
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

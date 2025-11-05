import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
// import ReactMarkdown from "react-markdown";
import Navbar from "../components/layout/Navbar";
import noteService from "../services/noteService";
import projectService from "../services/projectService";
import CommentSection from "../components/comments/CommentSection";
import "../styles/pages/note-show.css";

const NoteShowPage = () => {
  const { id } = useParams(); // ID de la note
  const navigate = useNavigate();
  
  const [note, setNote] = useState(null);
  const [project, setProject] = useState(null);
  const [otherNotes, setOtherNotes] = useState([]);
  const [members, setMembers] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  // État pour l'édition de la note
  const [isEditingNote, setIsEditingNote] = useState(false);
  const [editNoteData, setEditNoteData] = useState({
    title: "",
    content: "",
  });

  // État formulaire création note
  const [createFormData, setCreateFormData] = useState({
    title: "",
    content: "",
  });

  useEffect(() => {
    loadData();
    loadCurrentUser();
  }, [id]);

  const loadCurrentUser = async () => {
    try {
      // On récupère l'utilisateur depuis le localStorage (mis par AuthContext)
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const userData = JSON.parse(userStr);
        setCurrentUser(userData);
      }
    } catch (error) {
      console.error("Erreur chargement utilisateur:", error);
    }
  };

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // 1. Charger TOUTES les notes (on ne peut pas charger une seule note directement)
      // On va devoir charger par projet, donc on doit d'abord trouver à quel projet appartient la note
      // Pour cela, on va utiliser une astuce : charger tous les projets et trouver celui qui contient notre note
      
      // ALTERNATIVE : Charger depuis le localStorage si on vient de ProjectShowPage
      const tempProject = sessionStorage.getItem('currentProject');
      let projectData;
      
      if (tempProject) {
        projectData = JSON.parse(tempProject);
      } else {
        // Si pas de projet en session, on doit le trouver
        // Pour l'instant, on va afficher une erreur
        throw new Error("Impossible de charger la note. Veuillez revenir au projet.");
      }
      
      setProject(projectData);
      
      // 2. Charger TOUTES les notes du projet
      const allNotes = await noteService.getByProject(projectData.id);
      
      // 3. Trouver LA note qu'on veut
      const currentNote = allNotes.find(n => n.id === parseInt(id));
      
      if (!currentNote) {
        throw new Error("Note non trouvée");
      }
      
      setNote(currentNote);
      
      // 4. Filtrer pour avoir les "autres notes" (sauf la note actuelle)
      const filtered = allNotes.filter(n => n.id !== parseInt(id));
      setOtherNotes(filtered);
      
      // 5. Charger les membres du projet
      try {
        const membersData = await projectService.getMembers(projectData.id);
        setMembers(membersData);
      } catch (e) {
        console.warn("Impossible de charger les membres");
        setMembers([]);
      }
    } catch (error) {
      console.error("Erreur:", error);
      setError(error.message || "Note introuvable");
    } finally {
      setLoading(false);
    }
  };

  // Permissions
  const canEditNote = () => {
    if (!currentUser || !note) return false;
    // Auteur ou Senior+ peut modifier
    return (
      note.author === currentUser.id ||
      ["senior", "lead", "admin"].includes(currentUser.role)
    );
  };

  const canDeleteNote = () => {
    if (!currentUser || !note) return false;
    // Seul l'auteur ou Lead+ peut supprimer
    return (
      note.author === currentUser.id ||
      ["lead", "admin"].includes(currentUser.role)
    );
  };

  // Édition de la note
  const startEditNote = () => {
    setEditNoteData({
      title: note.title,
      content: note.content,
    });
    setIsEditingNote(true);
  };

  const cancelEditNote = () => {
    setIsEditingNote(false);
    setEditNoteData({ title: "", content: "" });
  };

  const handleEditNote = async (e) => {
    e.preventDefault();
    if (!editNoteData.title.trim() || !editNoteData.content.trim()) {
      alert("Titre et contenu obligatoires");
      return;
    }

    try {
      const updated = await noteService.update(note.id, editNoteData);
      setNote(updated);
      setIsEditingNote(false);
      alert("Note modifiée avec succès");
    } catch (error) {
      console.error("Erreur modification note:", error);
      alert("Erreur lors de la modification");
    }
  };

  // Suppression de la note
  const handleDeleteNote = async () => {
    if (!window.confirm("Voulez-vous vraiment supprimer cette note ?")) {
      return;
    }

    try {
      await noteService.delete(note.id);
      alert("Note supprimée avec succès");
      navigate(`/projects/${project.id}`);
    } catch (error) {
      console.error("Erreur suppression note:", error);
      alert("Erreur lors de la suppression");
    }
  };

  // Création d'une nouvelle note
  const handleCreateNote = async (e) => {
    e.preventDefault();
    if (!createFormData.title.trim() || !createFormData.content.trim()) {
      alert("Titre et contenu obligatoires");
      return;
    }

    try {
      const newNote = await noteService.create({
        ...createFormData,
        project: project.id,
        status: "publie",
      });
      
      setCreateFormData({ title: "", content: "" });
      setShowCreateForm(false);
      
      // Recharger les données pour afficher la nouvelle note
      loadData();
      
      alert("Note créée avec succès");
    } catch (error) {
      console.error("Erreur création note:", error);
      alert("Erreur lors de la création");
    }
  };

  if (loading) {
    return (
      <div className="note-show-page">
        <Navbar />
        <div className="loading">Chargement...</div>
      </div>
    );
  }

  if (error || !note) {
    return (
      <div className="note-show-page">
        <Navbar />
        <div className="error-message">{error || "Note introuvable"}</div>
      </div>
    );
  }

  return (
    <div className="note-show-page">
      <Navbar />
      
      <div className="note-show-page__container">
        {/* PARTIE GAUCHE - Note principale */}
        <div className="note-show-page__main">
          {isEditingNote ? (
            // MODE ÉDITION
            <div className="note-edit-form">
              <h2>Modifier la note</h2>
              <form onSubmit={handleEditNote}>
                <div className="form-group">
                  <label>Titre</label>
                  <input
                    type="text"
                    value={editNoteData.title}
                    onChange={(e) =>
                      setEditNoteData({ ...editNoteData, title: e.target.value })
                    }
                    placeholder="Titre de la note"
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>Contenu</label>
                  <textarea
                    value={editNoteData.content}
                    onChange={(e) =>
                      setEditNoteData({ ...editNoteData, content: e.target.value })
                    }
                    placeholder="Contenu de la note"
                    rows="10"
                    required
                  />
                </div>
                
                <div className="form-actions">
                  <button type="submit" className="btn btn-primary">
                    Enregistrer
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={cancelEditNote}
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          ) : (
            // MODE AFFICHAGE
            <>
              <div className="note-header">
                <h1 className="note-header__title">{note.title}</h1>
                
                <div className="note-header__meta">
                  <span className="note-header__author">
                    {note.author_username}
                  </span>
                  <span className="note-header__separator">•</span>
                  <span className="note-header__date">
                    {new Date(note.created_at).toLocaleDateString("fr-FR")}
                  </span>
                  {note.is_edited && (
                    <>
                      <span className="note-header__separator">•</span>
                      <span className="note-header__edited">(modifiée)</span>
                    </>
                  )}
                </div>
                
                {(canEditNote() || canDeleteNote()) && (
                  <div className="note-header__actions">
                    {canEditNote() && (
                      <button
                        className="btn btn-edit"
                        onClick={startEditNote}
                      >
                        Modifier
                      </button>
                    )}
                    {canDeleteNote() && (
                      <button
                        className="btn btn-delete"
                        onClick={handleDeleteNote}
                      >
                        Supprimer
                      </button>
                    )}
                  </div>
                )}
              </div>

              <div className="note-comments">
                <h3>Commentaires</h3>
                <CommentSection noteId={note.id} />
              </div>
            </>
          )}
        </div>

        {/* PARTIE DROITE - Sidebar */}
        <div className="note-show-page__sidebar">
          {/* Info projet */}
          {project && (
            <div className="sidebar-section">
              <div className="sidebar-section__header">
                <h3 className="sidebar-section__title">Projet</h3>
              </div>
              
              <div className="project-info">
                <h4 
                  className="project-info__name"
                  onClick={() => navigate(`/projects/${project.id}`)}
                  style={{ cursor: "pointer" }}
                >
                  {project.name}
                </h4>
                
                {members.length > 0 && (
                  <div className="project-members">
                    <p className="members-label">Membres :</p>
                    <ul className="members-list">
                      {members.map((member) => (
                        <li key={member.id} className="member-item">
                          {member.username}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Autres notes du projet */}
          <div className="sidebar-section">
            <div className="sidebar-section__header">
              <h3 className="sidebar-section__title">Notes du projet</h3>
              <button
                className="btn-toggle-form"
                onClick={() => setShowCreateForm(!showCreateForm)}
              >
                {showCreateForm ? "−" : "+"}
              </button>
            </div>

            {/* Formulaire création note */}
            {showCreateForm && (
              <form className="create-note-form" onSubmit={handleCreateNote}>
                <input
                  type="text"
                  placeholder="Titre"
                  value={createFormData.title}
                  onChange={(e) =>
                    setCreateFormData({ ...createFormData, title: e.target.value })
                  }
                  required
                />
                <textarea
                  placeholder="Contenu"
                  value={createFormData.content}
                  onChange={(e) =>
                    setCreateFormData({ ...createFormData, content: e.target.value })
                  }
                  rows="4"
                  required
                />
                <button type="submit" className="btn btn-primary btn-sm">
                  Créer
                </button>
              </form>
            )}

            {/* Liste des autres notes */}
            <div className="notes-list">
              {otherNotes.length > 0 ? (
                otherNotes.map((n) => (
                  <div
                    key={n.id}
                    className="note-item"
                    onClick={() => navigate(`/notes/${n.id}`)}
                  >
                    <span className="note-item__icon">□</span>
                    <span className="note-item__title">{n.title}</span>
                  </div>
                ))
              ) : (
                <p className="empty-message">Aucune autre note</p>
              )}

              {/* Note actuelle (indiquée) */}
              <div className="note-item note-item--current">
                <span className="note-item__icon">■</span>
                <span className="note-item__title">{note.title}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NoteShowPage;
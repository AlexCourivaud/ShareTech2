// composants react
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

// composants navbar, api projet, api note
import Navbar from '../components/layout/Navbar';
import projectService from '../services/projectService';
import noteService from '../services/noteService';

// composant css
import '../styles/pages/project-show.css';

// constantes
const ProjectShowPage = () => {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [notes, setNotes] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // chargement des données
  useEffect(() => {
    loadData(); 
  }, [id]);

  const loadData = async () => {
    console.log('ID du projet:', id); // TODO a suppr
    try {
      setError(null);
      
      const projectData = await projectService.getById(id);
      setProject(projectData);

      try {
        const notesData = await noteService.getByProject(id);
        console.log('Notes reçues:', notesData); // TODO a suppr

        setNotes(notesData);
      } catch (e) {
        console.warn('Impossible de charger les notes');
        setNotes([]);
      }

      try {
        const membersData = await projectService.getMembers(id);
        setMembers(membersData);
      } catch (e) {
        console.warn('Impossible de charger les membres');
        setMembers([]);
      }

    } catch (error) {
      console.error('Erreur:', error);
      setError('Projet introuvable');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="project-show-page">
      <Navbar />
      <div className="project-show-page__container">
        <p>Chargement...</p>
      </div>
    </div>
  );

  if (error || !project) return (
    <div className="project-show-page">
      <Navbar />
      <div className="project-show-page__container">
        <p style={{ color: 'red' }}>{error || 'Projet introuvable'}</p>
      </div>
    </div>
  );

  return (
    <div className="project-show-page">
      <Navbar />
      
      <div className="project-show-page__container">
        <div className="project-show-page__header">
          <div>
            <h1>{project.name}</h1>
            <p className="text-muted">{project.description}</p>
          </div>
          <div className="project-show-page__participants">
            👤 {members.length} participant(s)
          </div>
        </div>

        <div className="project-show-page__notes">
          <h2>📝 Notes ({notes.length})</h2>
          <div className="project-show-page__card">
            {notes.length > 0 ? (
              notes.map(note => (
                <div key={note.id} className="note-item">
                  <h4>{note.title}</h4>
                  <p className="text-muted text-sm">
                    {note.excerpt || note.content?.substring(0, 150)}...
                  </p>
                </div>
              ))
            ) : (
              <p className="text-muted">Aucune note</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectShowPage;
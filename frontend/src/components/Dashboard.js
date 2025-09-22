import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const [projects, setProjects] = useState([]);
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [projectsData, notesData] = await Promise.all([
        ApiService.fetchProjects(),
        ApiService.fetchNotes()
      ]);
      
      setProjects(projectsData);
      setNotes(notesData);
      setLoading(false);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Chargement...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>ShareTech Dashboard</h1>
        <div className="search-bar">
          <input type="text" placeholder="Rechercher..." />
        </div>
        <nav className="navbar">
          <button className="nav-btn active">Dashboard</button>
          <button className="nav-btn">Notifications</button>
          <button className="nav-btn">Profil</button>
        </nav>
      </header>

      <main className="dashboard-content">
        <div className="dashboard-grid">
          <section className="projects-section">
            <h2>Vos Projets</h2>
            <div className="projects-list">
              {projects.map(project => (
                <div key={project.id} className="project-card">
                  <h3>{project.name}</h3>
                  <p>{project.description}</p>
                  <div className="project-meta">
                    <span>Créé par: {project.created_by?.username}</span>
                    <span>Membres: {project.members?.length || 0}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="favorites-section">
            <h2>Notes Récentes</h2>
            <div className="notes-list">
              {notes.map(note => (
                <div key={note.id} className="note-card">
                  <h4>{note.title}</h4>
                  <p>{note.content.substring(0, 100)}...</p>
                  <div className="note-meta">
                    <span>Projet: {note.project?.name}</span>
                    <span>Par: {note.author?.username}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
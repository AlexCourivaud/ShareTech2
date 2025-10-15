import React from 'react';
import '../styles/pages/home.css';

const HomePage = () => {
  return (
    <div className="home-page">
      <div className="home-page__container">
        <div className="home-page__hero">
          <h1 className="home-page__title">ShareTech</h1>
          <p className="home-page__slogan">
            Centralisez vos connaissances et optimisez votre collaboration
          </p>
          <a href="/login" className="home-page__cta">
            Se connecter
          </a>
        </div>

        <div className="home-page__features">
          <div className="home-page__feature">
            <h3>📝 Documentation</h3>
            <p>Centralisez toutes vos notes techniques en un seul endroit</p>
          </div>
          <div className="home-page__feature">
            <h3>✅ Gestion de tâches</h3>
            <p>Suivez l'avancement de vos projets en temps réel</p>
          </div>
          <div className="home-page__feature">
            <h3>👥 Collaboration</h3>
            <p>Travaillez ensemble efficacement sur vos projets</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
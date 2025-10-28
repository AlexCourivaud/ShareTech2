import React from "react";
import "../styles/pages/home.css";

const HomePage = () => {
  return (
    <div className="home-page">
      <div className="home-page__container">
        <div className="home-page__hero">
          <h1 className="home-page__title">ShareTech</h1>
          <p className="home-page__slogan">
            Le partage pour avancer ensemble !
          </p>
          <a href="/login" className="home-page__cta">
            Se connecter
          </a>
        </div>
        <div className="home-page__feature">
          <h3>Gestion de projet</h3>
          <p>
            ShareTech est une application développée spécifiquement pour
            l'enteprise Memory. Venez partager et travailler ensemble.
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;

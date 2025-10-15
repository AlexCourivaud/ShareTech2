import React from 'react';
import ReactDOM from 'react-dom/client';

// Import des CSS dans l'ordre
import './styles/variables.css';  // Variables d'abord
import './styles/reset.css';      // Reset ensuite
import './styles/utilities.css';  // Utilitaires
import './index.css';             // Styles globaux React (existe déjà)
import './App.css';               // Styles App (existe déjà)

import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

reportWebVitals();
import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import EtudiantsList from "./pages/EtudiantsList";
import CoursProfesseur from "./pages/CoursProfesseur";
import EmploiEtudiant from "./pages/EmploiEtudiant";
import CoursForm from "./pages/CoursForm";
import ClasseForm from "./pages/ClasseForm";
import './styles/Global.css'; // Importation du fichier CSS pour cette page

import EtudiantForm from "./pages/EtudiantForm";
import ProfesseurForm from "./pages/ProfesseurForm";
import EmploiDuTempsForm from "./pages/EmploiDuTempsForm";

const App = () => {
  return (
    <Router>
      {/* On déplace le hook useLocation() à l'intérieur du Router */}
      <NavBar />
      <Routes>
        <Route path="/" element={<h2 className="welcome">Bienvenue dans l'application de gestion de l'école 🎓</h2>} />
        <Route path="/professeur/:profId/cours" element={<CoursProfesseur />} />
        <Route path="/etudiant/:etudiantId/emploi" element={<EmploiEtudiant />} />
        <Route path="/classe/:classeId/etudiants" element={<EtudiantsList />} />
        
        {/* Routes pour les formulaires */}
        <Route path="/cours-form" element={<CoursForm />} />
        <Route path="/classe-form" element={<ClasseForm />} />
        <Route path="/etudiant-form" element={<EtudiantForm />} />
        <Route path="/professeurs-form" element={<ProfesseurForm />} />
        <Route path="/emploi-form" element={<EmploiDuTempsForm />} />
      </Routes>
    </Router>
  );
};

const NavBar = () => {
  const location = useLocation(); // Utilisation correcte du hook à l'intérieur du Router
  return (
    <nav className="navbar">
      <h1>📚 Gestion Scolaire</h1>
      <ul>
        <li><Link to="/" className={location.pathname === '/' ? 'active' : ''}>Accueil</Link></li>
        <li><Link to="/etudiant/emploi" className={location.pathname.includes('/etudiant') ? 'active' : ''}>Emploi du temps Étudiant</Link></li>
        <li><Link to="/classe/etudiants" className={location.pathname.includes('/classe') ? 'active' : ''}>Liste des Étudiants</Link></li>
        <li><Link to="/cours-form" className={location.pathname === '/cours-form' ? 'active' : ''}>Ajouter un cours</Link></li>
        <li><Link to="/classe-form" className={location.pathname === '/classe-form' ? 'active' : ''}>Ajouter une classe</Link></li>
        <li><Link to="/professeurs-form" className={location.pathname === '/professeurs-form' ? 'active' : ''}>Ajouter un(e) professeur</Link></li>
        <li><Link to="/etudiant-form" className={location.pathname === '/etudiant-form' ? 'active' : ''}>Ajouter un(e) étudiant(e)</Link></li>
        <li><Link to="/emploi-form" className={location.pathname === '/emploi-form' ? 'active' : ''}>Créer un emploi du temps</Link></li>
      </ul>
    </nav>
  );
};

export default App;

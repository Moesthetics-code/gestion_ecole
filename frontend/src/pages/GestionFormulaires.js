import React from "react";
import CoursForm from "./CoursForm";
import ClasseForm from "./ClasseForm";
import EmploiDuTempsForm from "./EmploiDuTempsForm";
import "../styles/GestionFormulaires.css";

const GestionFormulaires = () => {
  return (
    <div className="gestion-container">
      <h2>📋 Gestion des Cours et Emplois du Temps</h2>
      <div className="form-section">
        <CoursForm />
        <ClasseForm />
        <EmploiDuTempsForm />
      </div>
    </div>
  );
};

export default GestionFormulaires;

import React, { useState, useEffect } from "react";

const AssignCoursForm = ({ onCoursAssigned }) => {
  const [professeurs, setProfesseurs] = useState([]);
  const [cours, setCours] = useState([]);
  const [selectedProfesseur, setSelectedProfesseur] = useState("");
  const [selectedCours, setSelectedCours] = useState("");

  useEffect(() => {
    // Charger la liste des professeurs
    fetch("http://localhost:5000/professeurs/professeurs")
      .then((response) => response.json())
      .then((data) => setProfesseurs(data))
      .catch((error) => console.error("Erreur lors du chargement des professeurs :", error));

    // Charger la liste des cours
    fetch("http://localhost:5000/cours/cours")
      .then((response) => response.json())
      .then((data) => setCours(data))
      .catch((error) => console.error("Erreur lors du chargement des cours :", error));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedProfesseur || !selectedCours) {
      alert("Veuillez sélectionner un professeur et un cours.");
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:5000/professeurs/professeurs/${selectedProfesseur}/cours/${selectedCours}`,
        { method: "POST" }
      );

      if (response.ok) {
        setSelectedProfesseur("");
        setSelectedCours("");
        onCoursAssigned();
      } else {
        console.error("Erreur lors de l'assignation du cours");
      }
    } catch (error) {
      console.error("Erreur de connexion :", error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Professeur :</label>
        <select value={selectedProfesseur} onChange={(e) => setSelectedProfesseur(e.target.value)} required>
          <option value="">Sélectionnez un professeur</option>
          {professeurs.map((prof) => (
            <option key={prof.id} value={prof.id}>
              {prof.nom}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label>Cours :</label>
        <select value={selectedCours} onChange={(e) => setSelectedCours(e.target.value)} required>
          <option value="">Sélectionnez un cours</option>
          {cours.map((cours) => (
            <option key={cours.id} value={cours.id}>
              {cours.nom}
            </option>
          ))}
        </select>
      </div>
      <button type="submit">Assigner Cours</button>
    </form>
  );
};

export default AssignCoursForm;

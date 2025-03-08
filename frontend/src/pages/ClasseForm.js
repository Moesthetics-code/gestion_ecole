// src/components/ClasseForm.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/ClasseForm.css";


// Utilisation du gateway comme point d'entrée
const API_GATEWAY_URL = "http://localhost:5000/classes/classes";

const ClasseForm = () => {
  const [classes, setClasses] = useState([]);
  const [newClasse, setNewClasse] = useState({ nom: "", niveau: "" });

  // Récupérer la liste des classes via le gateway
  useEffect(() => {
    axios
      .get(API_GATEWAY_URL)
      .then((response) => setClasses(response.data))
      .catch((error) => console.error("Erreur lors de la récupération des classes:", error));
  }, []);

  // Ajouter une nouvelle classe via le gateway
  const handleSubmit = (e) => {
    e.preventDefault();
    axios
      .post(API_GATEWAY_URL, newClasse)
      .then((response) => {
        setClasses([...classes, response.data]); // Ajouter la nouvelle classe à la liste
        setNewClasse({ nom: "", niveau: "" });
      })
      .catch((error) => console.error("Erreur lors de l'ajout de la classe:", error));
  };

  // Supprimer une classe via le gateway
  const handleDelete = (id) => {
    axios
      .delete(`${API_GATEWAY_URL}/${id}`)
      .then(() => {
        setClasses(classes.filter((cls) => cls.id !== id));
      })
      .catch((error) => console.error("Erreur lors de la suppression de la classe:", error));
  };

  return (
    <div className="container">
  <h3>Ajouter une Classe</h3>
  <form onSubmit={handleSubmit}>
    <input
      type="text"
      value={newClasse.nom}
      onChange={(e) => setNewClasse({ ...newClasse, nom: e.target.value })}
      placeholder="Nom de la Classe"
      required
    />
    <input
      type="text"
      value={newClasse.niveau}
      onChange={(e) => setNewClasse({ ...newClasse, niveau: e.target.value })}
      placeholder="Niveau"
      required
    />
    <button type="submit">Ajouter Classe</button>
  </form>

  <h4>Liste des Classes</h4>
  <ul>
    {classes.map((cls) => (
      <li key={cls.id}>
        {cls.nom} (Niveau: {cls.niveau})
        <button onClick={() => handleDelete(cls.id)}>Supprimer</button>
      </li>
    ))}
  </ul>
</div>

  );
};

export default ClasseForm;

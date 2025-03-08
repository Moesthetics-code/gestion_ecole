import React, { useState, useEffect } from 'react';
import axios from 'axios';
import "../styles/CoursForm.css";

const CoursForm = () => {
  const [cours, setCours] = useState([]);
  const [classes, setClasses] = useState([]); // Ajout de l'état pour stocker les classes
  const [newCours, setNewCours] = useState({ nom: '', classe_id: '' });

  // Récupérer la liste des cours
  useEffect(() => {
    axios.get('http://localhost:5000/cours/cours')
      .then(response => setCours(response.data))
      .catch(error => {
        console.error(error);
        alert("Erreur lors de la récupération des cours.");
      });
  }, []);

  // Récupérer la liste des classes
  useEffect(() => {
    axios.get('http://localhost:5000/classes/classes')
      .then(response => setClasses(response.data))
      .catch(error => {
        console.error(error);
        alert("Erreur lors de la récupération des classes.");
      });
  }, []);

  // Gestion de la soumission du formulaire
  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5000/cours/cours', newCours)
      .then(response => {
        setCours([...cours, response.data]);  
        setNewCours({ nom: '', classe_id: '' }); // Réinitialisation du formulaire
      })
      .catch(error => {
        console.error(error);
        alert("Erreur lors de l'ajout du cours.");
      });
  };

  // Suppression d'un cours
  const handleDelete = (id) => {
    axios.delete(`http://localhost:5000/cours/cours/${id}`)
      .then(() => {
        setCours(cours.filter(course => course.id !== id));
      })
      .catch(error => console.error(error));
  };

  return (
    <div className="container">
      <h3>Ajouter un Cours</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={newCours.nom}
          onChange={(e) => setNewCours({ ...newCours, nom: e.target.value })}
          placeholder="Nom du Cours"
          required
        />
        
        {/* Sélection de la classe */}
        <select 
        value={newCours.classe_id} 
        onChange={(e) => setNewCours({ ...newCours, classe_id: Number(e.target.value) })} // Convertir en nombre
        required
      >

          <option value="">Sélectionner une classe</option>
          {classes.map(classe => (
            <option key={classe.id} value={classe.id}>
              {classe.nom} (Niveau: {classe.niveau})
            </option>
          ))}
        </select>

        <button type="submit">Ajouter Cours</button>
      </form>
      
      <h4>Liste des Cours</h4>
      <ul>
        {cours.map(course => (
          <li key={course.id}>
            {course.nom} (Classe ID: {course.classe_id})
            <button onClick={() => handleDelete(course.id)}>Supprimer</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CoursForm;

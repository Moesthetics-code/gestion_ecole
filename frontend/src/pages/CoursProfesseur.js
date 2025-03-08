import React, { useEffect, useState } from 'react';
import axios from 'axios';
//import '../styles/CoursProfesseur.css'; // Importation du fichier CSS pour cette page

function CoursProfesseur({ profId }) {
  const [cours, setCours] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`http://gateway:5000/professeurs/professeurs/${profId}/cours`)
      .then(response => {
        setCours(response.data);
      })
      .catch(error => {
        setError('Erreur lors de la récupération des cours');
      });
  }, [profId]);

  return (
    <div className="cours-professeur">
      <h1>Cours du Professeur</h1>
      {error && <div className="error">{error}</div>}
      {cours.length > 0 ? (
        <ul>
          {cours.map(course => (
            <li key={course.id}>{course.name}</li>
          ))}
        </ul>
      ) : (
        <p>Aucun cours trouvé pour ce professeur</p>
      )}
    </div>
  );
}

export default CoursProfesseur;

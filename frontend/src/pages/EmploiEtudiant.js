import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../styles/EmploiEtudiant.css'; // Importation du fichier CSS pour cette page

function EmploiEtudiant({ etudiantId }) {
  const [emploi, setEmploi] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`http://gateway:5000/etudiants/${etudiantId}/emplois_du_temps`)
      .then(response => {
        setEmploi(response.data);
      })
      .catch(error => {
        setError('Erreur lors de la récupération de l\'emploi du temps');
      });
  }, [etudiantId]);

  return (
    <div className="emploi-etudiant">
      <h1>Emploi du Temps de l'Étudiant</h1>
      {error && <div className="error">{error}</div>}
      {emploi.length > 0 ? (
        <ul>
          {emploi.map((session, index) => (
            <li key={index}>
              <p><strong>{session.jour}</strong>: {session.cours} - {session.horaire}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>Aucun emploi du temps trouvé pour cet étudiant</p>
      )}
    </div>
  );
}

export default EmploiEtudiant;

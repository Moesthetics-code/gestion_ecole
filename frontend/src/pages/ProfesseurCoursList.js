import React, { useState, useEffect } from "react";

const ProfesseurCoursList = ({ professeurId }) => {
  const [cours, setCours] = useState([]);
  const [professeurNom, setProfesseurNom] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchCours = async () => {
      try {
        const response = await fetch(`http://localhost:5000/professeurs/professeurs/${professeurId}/cours`);
        if (!response.ok) {
          throw new Error("Erreur lors de la récupération des cours");
        }

        const data = await response.json();
        setProfesseurNom(data.professeur);
        setCours(data.cours);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCours();
  }, [professeurId]);

  if (loading) return <p>Chargement des cours...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div>
      <h3>Cours de {professeurNom}</h3>
      {cours.length > 0 ? (
        <ul>
          {cours.map((coursItem) => (
            <li key={coursItem.id}>{coursItem.nom}</li>
          ))}
        </ul>
      ) : (
        <p>Aucun cours assigné à ce professeur.</p>
      )}
    </div>
  );
};

export default ProfesseurCoursList;

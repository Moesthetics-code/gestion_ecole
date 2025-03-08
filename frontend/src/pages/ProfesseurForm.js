import React, { useState, useEffect } from "react";
import axios from "axios";

const ProfesseurForm = () => {
  const [nom, setNom] = useState("");
  const [specialite, setSpecialite] = useState("");
  const [professeurs, setProfesseurs] = useState([]); // ✅ Stocker la liste des professeurs
  const [message, setMessage] = useState({ type: "", text: "" });
  const [isLoading, setIsLoading] = useState(false);

  // ✅ Fonction pour récupérer la liste des professeurs
  const fetchProfesseurs = async () => {
    try {
      const response = await axios.get("http://localhost:5000/professeurs/professeurs");
      setProfesseurs(response.data);
    } catch (error) {
      console.error("Erreur lors de la récupération des professeurs :", error);
    }
  };

  // ✅ Charger la liste des professeurs au montage du composant
  useEffect(() => {
    fetchProfesseurs();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ type: "", text: "" });

    if (!nom.trim()) {
      setMessage({ type: "error", text: "Le champ 'Nom' est requis." });
      return;
    }

    const professeurData = {
      nom: nom.trim(),
      specialite: specialite.trim() || null,
    };

    setIsLoading(true);

    try {
      const response = await axios.post(
        "http://localhost:5000/professeurs/professeurs", // ✅ URL API
        professeurData,
        { headers: { "Content-Type": "application/json" } }
      );

      if (response.status === 201) {
        setMessage({ type: "success", text: "Professeur ajouté avec succès !" });
        setNom("");
        setSpecialite("");
        fetchProfesseurs(); // ✅ Recharger la liste après ajout
      }
    } catch (error) {
      let errorMessage = "Erreur lors de l'ajout du professeur.";
      if (error.response && error.response.data.message) {
        errorMessage = error.response.data.message;
      }
      setMessage({ type: "error", text: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>Ajouter un Professeur</h2>
      {message.text && (
        <p
          style={{ color: message.type === "error" ? "red" : "green", fontWeight: "bold", fontSize: "16px" }}
          aria-live="assertive"
        >
          {message.text}
        </p>
      )}
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="nom">Nom :</label>
          <input
            id="nom"
            type="text"
            value={nom}
            onChange={(e) => setNom(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        <div>
          <label htmlFor="specialite">Spécialité :</label>
          <input
            id="specialite"
            type="text"
            value={specialite}
            onChange={(e) => setSpecialite(e.target.value)}
            disabled={isLoading}
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Ajout en cours..." : "Ajouter"}
        </button>
      </form>

      <h3>Liste des Professeurs</h3>
      <ul>
        {professeurs.length > 0 ? (
          professeurs.map((prof) => (
            <li key={prof.id}>
              <strong>{prof.nom}</strong> - {prof.specialite || "Aucune spécialité"}
            </li>
          ))
        ) : (
          <p>Aucun professeur trouvé.</p>
        )}
      </ul>
    </div>
  );
};

export default ProfesseurForm;

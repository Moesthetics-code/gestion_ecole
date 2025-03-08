import { useState, useEffect } from "react";
import axios from "axios";

const EtudiantForm = () => {
  const [etudiant, setEtudiant] = useState({ nom: "", classe_id: "" });
  const [classes, setClasses] = useState([]);
  const [etudiants, setEtudiants] = useState([]); // État pour la liste des étudiants
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Récupérer la liste des classes
  useEffect(() => {
    axios
      .get("http://localhost:5000/classes/classes")
      .then((response) => setClasses(response.data))
      .catch(() => setError("Erreur lors de la récupération des classes"));
  }, []);

  // Récupérer la liste des étudiants
  const fetchEtudiants = () => {
    axios
      .get("http://localhost:5000/etudiants/etudiants")
      .then((response) => setEtudiants(response.data))
      .catch(() => setError("Erreur lors de la récupération des étudiants"));
  };

  // Charger les étudiants au montage
  useEffect(() => {
    fetchEtudiants();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await axios.post("http://localhost:5000/etudiants/etudiants", {
        nom: etudiant.nom,
        classe_id: parseInt(etudiant.classe_id, 10),
      });

      if (response.status === 201) {
        setEtudiant({ nom: "", classe_id: "" }); // Réinitialisation du formulaire
        fetchEtudiants(); // Rafraîchir la liste des étudiants
      }
    } catch (error) {
      setError("Erreur lors de l'ajout de l'étudiant");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-4 max-w-lg mx-auto">
      <form onSubmit={handleSubmit} className="space-y-3 bg-white p-4 shadow-md rounded">
        {error && <p className="text-red-500">{error}</p>}

        <input
          type="text"
          value={etudiant.nom}
          onChange={(e) => setEtudiant({ ...etudiant, nom: e.target.value })}
          placeholder="Nom de l'étudiant"
          required
          className="w-full p-2 border rounded"
        />

        <select
          value={etudiant.classe_id}
          onChange={(e) => setEtudiant({ ...etudiant, classe_id: e.target.value })}
          required
          className="w-full p-2 border rounded"
        >
          <option value="">Sélectionner une classe</option>
          {classes.map((classe) => (
            <option key={classe.id} value={classe.id}>
              {classe.nom}
            </option>
          ))}
        </select>

        <button
          type="submit"
          className={`w-full py-2 rounded ${isSubmitting ? "bg-gray-400" : "bg-blue-500 hover:bg-blue-600"} text-white`}
          disabled={isSubmitting}
        >
          {isSubmitting ? "Ajout en cours..." : "Ajouter Étudiant"}
        </button>
      </form>

      {/* Affichage de la liste des étudiants */}
      <div className="mt-6">
        <h2 className="text-xl font-semibold">Liste des Étudiants</h2>
        {etudiants.length === 0 ? (
          <p className="text-gray-500">Aucun étudiant trouvé.</p>
        ) : (
          <ul className="mt-3 space-y-2">
            {etudiants.map((etudiant) => (
              <li key={etudiant.id} className="p-2 border rounded bg-gray-100">
                {etudiant.nom} - Classe ID: {etudiant.classe_id}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default EtudiantForm;

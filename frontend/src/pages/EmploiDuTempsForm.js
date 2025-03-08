import React, { useState, useEffect } from "react";
import axios from "axios";

const API_BASE_URL = "http://localhost:5000/emplois_du_temps/emplois_du_temps";
const CLASSES_API = "http://localhost:5000/classes/classes";
const COURS_API = "http://localhost:5000/cours/cours";
const PROFESSEURS_API = "http://localhost:5000/professeurs/professeurs";

const EmploiDuTempsForm = () => {
  const [emploi, setEmploi] = useState({
    id: "", // Ajouté si nécessaire
    classe_id: "",
    cours_id: "",
    professeur_id: "",
    jour: "",
    heure_debut: "",
    heure_fin: "",
  });

  const [emplois, setEmplois] = useState([]);
  const [classes, setClasses] = useState([]);
  const [cours, setCours] = useState([]);
  const [professeurs, setProfesseurs] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(""); // État pour gérer les erreurs

  useEffect(() => {
    fetchAllData();
  }, []);

  // 🔹 Charger toutes les données en parallèle
  const fetchAllData = async () => {
    try {
      const [emploisRes, classesRes, coursRes, professeursRes] = await Promise.all([
        axios.get(API_BASE_URL),
        axios.get(CLASSES_API),
        axios.get(COURS_API),
        axios.get(PROFESSEURS_API),
      ]);

      setEmplois(emploisRes.data);
      setClasses(classesRes.data);
      setCours(coursRes.data);
      setProfesseurs(professeursRes.data);
    } catch (error) {
      setError("Erreur lors du chargement des données");
      console.error("Erreur lors du chargement des données:", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!emploi.classe_id || !emploi.cours_id || !emploi.professeur_id || !emploi.jour || !emploi.heure_debut || !emploi.heure_fin) {
      setError("Veuillez remplir tous les champs.");
      return;
    }

    try {
      const request = editingId
        ? axios.put(`${API_BASE_URL}/${editingId}`, emploi)
        : axios.post(API_BASE_URL, emploi);

      await request;
      alert(editingId ? "Emploi du temps mis à jour avec succès" : "Emploi du temps ajouté avec succès");
      resetForm();
      fetchAllData(); // Recharger toutes les données
    } catch (error) {
      setError("Erreur lors de l'opération");
      console.error("Erreur lors de l'opération:", error);
    }
  };

  const handleEdit = (emploi) => {
    setEmploi(emploi);
    setEditingId(emploi.id);
  };

  const handleDelete = async (id) => {
    if (window.confirm("Voulez-vous vraiment supprimer cet emploi du temps ?")) {
      try {
        await axios.delete(`${API_BASE_URL}/${id}`);
        alert("Emploi du temps supprimé avec succès");
        fetchAllData(); // Recharger toutes les données après suppression
      } catch (error) {
        setError("Erreur lors de la suppression");
        console.error("Erreur lors de la suppression:", error);
      }
    }
  };

  const resetForm = () => {
    setEmploi({
      classe_id: "",
      cours_id: "",
      professeur_id: "",
      jour: "",
      heure_debut: "",
      heure_fin: "",
    });
    setEditingId(null);
    setError(""); // Réinitialiser l'erreur lors de la réinitialisation du formulaire
  };

  return (
    <div className="max-w-lg mx-auto bg-white p-6 rounded-lg shadow-md mt-10">
      <h3 className="text-xl font-bold text-center mb-4">{editingId ? "Modifier" : "Ajouter"} un Emploi du Temps</h3>
      
      {error && <div className="text-red-500 text-center mb-4">{error}</div>} {/* Affichage des erreurs */}

      <form onSubmit={handleSubmit} className="space-y-3">
        {/* 🔹 Sélection de la classe */}
        <select
          className="w-full p-2 border rounded"
          value={emploi.classe_id}
          onChange={(e) => setEmploi({ ...emploi, classe_id: e.target.value })}
          required
        >
          <option value="">Sélectionner une classe</option>
          {classes.map((classe) => (
            <option key={classe.id} value={classe.id}>{classe.nom}</option>
          ))}
        </select>

        {/* 🔹 Sélection du cours */}
        <select
          className="w-full p-2 border rounded"
          value={emploi.cours_id}
          onChange={(e) => setEmploi({ ...emploi, cours_id: e.target.value })}
          required
        >
          <option value="">Sélectionner un cours</option>
          {cours.map((cours) => (
            <option key={cours.id} value={cours.id}>{cours.nom}</option>
          ))}
        </select>

        {/* 🔹 Sélection du professeur */}
        <select
          className="w-full p-2 border rounded"
          value={emploi.professeur_id}
          onChange={(e) => setEmploi({ ...emploi, professeur_id: e.target.value })}
          required
        >
          <option value="">Sélectionner un professeur</option>
          {professeurs.map((prof) => (
            <option key={prof.id} value={prof.id}>{prof.nom} {prof.prenom}</option>
          ))}
        </select>

        <input
          className="w-full p-2 border rounded"
          type="text"
          value={emploi.jour}
          onChange={(e) => setEmploi({ ...emploi, jour: e.target.value })}
          placeholder="Jour"
          required
        />

        <input
          className="w-full p-2 border rounded"
          type="time"
          value={emploi.heure_debut}
          onChange={(e) => setEmploi({ ...emploi, heure_debut: e.target.value })}
          required
        />

        <input
          className="w-full p-2 border rounded"
          type="time"
          value={emploi.heure_fin}
          onChange={(e) => setEmploi({ ...emploi, heure_fin: e.target.value })}
          required
        />

        <div className="flex gap-2">
          <button type="submit" className="w-full bg-green-500 text-white py-2 rounded hover:bg-green-600">
            {editingId ? "Modifier" : "Ajouter"}
          </button>
          {editingId && (
            <button type="button" className="w-full bg-gray-400 text-white py-2 rounded hover:bg-gray-500" onClick={resetForm}>
              Annuler
            </button>
          )}
        </div>
      </form>

      <h4 className="text-lg font-bold mt-6">Liste des Emplois du Temps</h4>
      <ul className="mt-4">
        {emplois.map((emploi) => (
          <li
            key={emploi.id}
            className="flex justify-between items-center bg-gray-100 p-3 rounded-md mb-2"
          >
            <span>
              {emploi.jour}, {emploi.heure_debut} - {emploi.heure_fin} | Cours: {emploi.cours_id} | Prof: {emploi.professeur_id}
            </span>
            <div className="flex gap-2">
              <button
                className="bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                onClick={() => handleEdit(emploi)}
              >
                Modifier
              </button>
              <button
                className="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600"
                onClick={() => handleDelete(emploi.id)}
              >
                Supprimer
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default EmploiDuTempsForm;

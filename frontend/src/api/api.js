const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

/**
 * Récupère la liste des étudiants d'une classe avec le nom de la classe
 * @param {number} classeId 
 * @returns {Promise<Array>}
 */
export async function getEtudiantsParClasse(classeId) {
    try {
        const response = await fetch(`${API_URL}/classes/classes/${classeId}/etudiants`);
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des étudiants");
        }
        return await response.json();
    } catch (error) {
        console.error("Erreur API:", error);
        return [];
    }
}

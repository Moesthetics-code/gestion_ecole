import React, { useEffect, useState } from "react";
import { getEtudiantsParClasse } from "../api/api";

const EtudiantsList = ({ classeId }) => {
    const [etudiants, setEtudiants] = useState([]);

    useEffect(() => {
        async function fetchData() {
            const data = await getEtudiantsParClasse(classeId);
            setEtudiants(data);
        }
        fetchData();
    }, [classeId]);

    return (
        <div>
            <h2>Liste des étudiants de la classe {etudiants.length > 0 ? etudiants[0].nom_classe : "..."}</h2>
            <ul>
                {etudiants.map(etudiant => (
                    <li key={etudiant.id}>
                        {etudiant.nom} {etudiant.prenom} - Classe : {etudiant.nom_classe}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default EtudiantsList;

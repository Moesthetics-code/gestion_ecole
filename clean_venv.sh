#!/bin/bash

# Chemin vers le dossier contenant les microservices
SERVICES_DIR="services"

# Vérifier si le dossier services existe
if [ ! -d "$SERVICES_DIR" ]; then
    echo "Le dossier $SERVICES_DIR n'existe pas."
    exit 1
fi

# Parcourir chaque dossier dans services/
for service in "$SERVICES_DIR"/*; do
    if [ -d "$service/venv" ]; then
        echo "Suppression du dossier venv dans $service"
        rm -rf "$service/venv"
    else
        echo "Aucun dossier venv trouvé dans $service"
    fi
done

echo "Nettoyage terminé."
 
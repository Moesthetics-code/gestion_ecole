import os

# Définition des URL des microservices
MICROSERVICES = {
    "classes": os.getenv("CLASSES_SERVICE_URL", "http://microservice_classes:5001"),
    "cours": os.getenv("COURS_SERVICE_URL", "http://microservice_cours:5002"),
    "etudiants": os.getenv("ETUDIANTS_SERVICE_URL", "http://microservice_etudiants:5003"),
    "professeurs": os.getenv("PROFESSEURS_SERVICE_URL", "http://microservice_professeurs:5004"),
    "emplois_du_temps": os.getenv("EMPLOIS_DU_TEMPS_SERVICE_URL", "http://microservice_emplois:5005"),
}

# Configuration générale
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "5000"))

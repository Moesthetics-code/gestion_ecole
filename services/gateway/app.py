from flask import Flask, request, jsonify
import requests
import config  # Import du fichier de configuration
import logging
from flask_cors import CORS

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
CORS(app)  # Autorise toutes les origines (à sécuriser en production)

MICROSERVICES = config.MICROSERVICES  # URLs des microservices
TIMEOUT = 5  # Timeout pour les requêtes HTTP

@app.route('/', methods=["GET"])
def home():
    return "Bienvenue sur le service Gateway!", 200

def make_request(url, timeout=TIMEOUT):
    """ Envoie une requête GET et gère les erreurs de manière centralisée. """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors de la requête {url}: {str(e)}")
        return {"error": "Erreur de communication avec le service distant"}, 500

@app.route('/bff/cours_details/<int:cours_id>', methods=["GET"])
def get_cours_details(cours_id):
    """ Récupère les détails d'un cours avec les informations de la classe associée. """
    cours_url = f"{MICROSERVICES['cours']}/cours/{cours_id}"
    cours_data, status = make_request(cours_url)
    
    if status != 200:
        return jsonify(cours_data), status

    classe_url = f"{MICROSERVICES['classes']}/classes/{cours_data.get('classe_id')}"
    classe_data, _ = make_request(classe_url)

    cours_data["classe"] = classe_data if "error" not in classe_data else None
    return jsonify(cours_data), 200

@app.route('/classes/<int:classe_id>/etudiants', methods=['GET'])
def get_etudiants_classe(classe_id):
    """ Récupère les étudiants d'une classe avec le nom de la classe. """
    etudiants_url = f"{MICROSERVICES['etudiants']}/etudiants?classe_id={classe_id}"
    etudiants_data, status = make_request(etudiants_url)

    if status != 200:
        return jsonify(etudiants_data), status

    classe_url = f"{MICROSERVICES['classes']}/classes/{classe_id}"
    classe_data, _ = make_request(classe_url)

    nom_classe = classe_data.get("nom", "Classe inconnue") if "error" not in classe_data else "Classe inconnue"

    for etudiant in etudiants_data:
        etudiant["nom_classe"] = nom_classe

    return jsonify(etudiants_data), 200

@app.route('/professeurs/<int:prof_id>/cours', methods=['GET'])
def get_cours_professeur(prof_id):
    """ Récupère la liste des cours enseignés par un professeur. """
    url = f"{MICROSERVICES['professeurs']}/professeurs/{prof_id}/cours"
    data, status = make_request(url)
    return jsonify(data), status

@app.route('/etudiants/<int:etudiant_id>/emplois_du_temps', methods=['GET'])
def get_emploi_etudiant(etudiant_id):
    """ Récupère l'emploi du temps d'un étudiant à partir de sa classe. """
    etudiant_url = f"{MICROSERVICES['etudiants']}/etudiants/{etudiant_id}"
    etudiant_data, status = make_request(etudiant_url)

    if status != 200:
        return jsonify(etudiant_data), status

    classe_id = etudiant_data.get("classe_id")
    if not classe_id:
        return jsonify({"error": "Aucune classe associée à cet étudiant"}), 400

    emploi_url = f"{MICROSERVICES['emplois_du_temps']}/emplois_du_temps?classe_id={classe_id}"
    emploi_data, status = make_request(emploi_url)
    
    return jsonify(emploi_data), status

@app.route('/<service>/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
def gateway(service, path):
    """ Proxy générique permettant de router les requêtes vers les microservices. """
    if service not in MICROSERVICES:
        return jsonify({"error": "Service non trouvé"}), 404

    service_url = f"{MICROSERVICES[service]}/{path}"
    try:
        response = requests.request(
            method=request.method,
            url=service_url,
            headers={k: v for k, v in request.headers if k.lower() != "host"},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=TIMEOUT
        )
        return response.content, response.status_code, response.headers.items()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors de la requête vers {service}: {str(e)}")
        return jsonify({"error": "Erreur de communication avec le service"}), 500

@app.route('/healthz', methods=['GET'])
def health_check():
    """ Vérifie si le BFF est actif. """
    return "OK", 200

@app.route('/ready', methods=['GET'])
def readiness_check():
    """ Vérifie si le BFF est prêt en testant la disponibilité des microservices. """
    unavailable_services = []

    for key, url in MICROSERVICES.items():
        _, status = make_request(url, timeout=2)
        if status != 200:
            logging.warning(f"Service {key} ({url}) indisponible.")
            unavailable_services.append(key)

    if unavailable_services:
        return jsonify({"error": f"Microservices indisponibles: {', '.join(unavailable_services)}"}), 503

    return "OK", 200

if __name__ == "__main__":
    app.run(host=config.GATEWAY_HOST, port=config.GATEWAY_PORT, debug=config.DEBUG)

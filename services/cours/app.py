from services.logging_config import setup_logging
import logging
import os
import requests
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flask_migrate import Migrate
from flask_cors import CORS

# === Configuration des logs ===
# Initialisation du logging
setup_logging()
logger = logging.getLogger("CoursService")

# === Initialisation de l'application Flask ===
app = Flask(__name__)
CORS(app)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Redington@db_cours:5432/cours_db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# === Modèle Cours ===
class Cours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    classe_id = db.Column(db.Integer, nullable=False)  # Pas de ForeignKey

with app.app_context():
    db.create_all()

# === Routes API ===
@app.route('/cours', methods=['GET'])
def get_all_cours():
    try:
        cours = Cours.query.all()
        logger.info("Liste des cours récupérée")
        return jsonify([{"id": c.id, "nom": c.nom, "classe_id": c.classe_id} for c in cours])
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des cours : {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/cours', methods=['POST'])
def add_cours():
    data = request.get_json()
    if not data or "nom" not in data or "classe_id" not in data:
        logger.warning("Requête invalide reçue pour l'ajout d'un cours")
        return jsonify({"message": "Données invalides"}), 400

    classe_url = f"http://microservice_classes:5001/classes/{data['classe_id']}"
    try:
        response = requests.get(classe_url)
        if response.status_code != 200:
            logger.warning(f"Classe introuvable pour ID {data['classe_id']}")
            return jsonify({"message": "Classe introuvable"}), 400
    except requests.RequestException as e:
        logger.error(f"Erreur de communication avec le microservice classe : {e}")
        return jsonify({"message": "Erreur de communication avec le microservice"}), 500

    try:
        new_cours = Cours(nom=data['nom'], classe_id=data['classe_id'])
        db.session.add(new_cours)
        db.session.commit()
        logger.info(f"Cours ajouté : {data['nom']} (Classe ID: {data['classe_id']})")
        return jsonify({"message": "Cours ajouté"}), 201
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du cours {data.get('nom')}: {e}")
        db.session.rollback()
        return jsonify({"message": "Erreur lors de l'ajout"}), 500
    
    
@app.route('/cours/<int:cours_id>', methods=['PUT'])
def update_cours(cours_id):
    data = request.get_json()
    cours = Cours.query.get(cours_id)
    
    if not cours:
        return jsonify({"message": "Cours non trouvé"}), 404

    if 'nom' in data:
        cours.nom = data['nom']
    if 'classe_id' in data:
        cours.classe_id = data['classe_id']
    
    try:
        db.session.commit()
        logger.info(f"Cours mis à jour : {cours.nom}")
        return jsonify({"message": "Cours mis à jour"}), 200
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du cours : {e}")
        db.session.rollback()
        return jsonify({"message": "Erreur lors de la mise à jour"}), 500


@app.route('/cours/<int:cours_id>', methods=['DELETE'])
def delete_cours(cours_id):
    cours = Cours.query.get(cours_id)
    
    if not cours:
        return jsonify({"message": "Cours non trouvé"}), 404

    try:
        db.session.delete(cours)
        db.session.commit()
        logger.info(f"Cours supprimé : {cours.nom}")
        return jsonify({"message": "Cours supprimé"}), 200
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du cours : {e}")
        db.session.rollback()
        return jsonify({"message": "Erreur lors de la suppression"}), 500


# === Configuration de Swagger UI ===
SWAGGER_URL = "/docs"
API_URL = "/swagger.yml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "API de gestion des cours"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/swagger.yml")
def swagger_file():
    try:
        file_path = os.path.join(os.getcwd(), "swagger.yml")
        if not os.path.exists(file_path):
            logger.warning("Fichier swagger.yml non trouvé")
            return jsonify({"message": "Fichier swagger.yml non trouvé"}), 404
        logger.info("Fichier swagger.yml envoyé")
        return send_file(file_path)
    except Exception as e:
        logger.error(f"Erreur lors de l'accès au fichier Swagger: {e}")
        return jsonify({"message": "Erreur interne"}), 500

# === Lancement de l'application ===
if __name__ == '__main__':
    with app.app_context():
        app.run(host='0.0.0.0', port=5002)

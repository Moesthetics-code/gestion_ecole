from logging_config import setup_logging
import logging
import os
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flask_migrate import Migrate
from flask_cors import CORS

# Initialisation du logging
setup_logging()
logger = logging.getLogger("ClassesService")

# === Initialisation de l'application Flask ===
app = Flask(__name__)
CORS(app)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Redington@db_classes:5432/classes_db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# === Modèle Classe ===
class Classe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False, unique=True)
    niveau = db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()  # À retirer si Flask-Migrate est utilisé

# === Routes API ===

# GET /classes
@app.route('/classes', methods=['GET'])
def get_classes():
    try:
        classes = Classe.query.all()
        logger.info("Liste des classes récupérée")
        return jsonify([{'id': classe.id, 'nom': classe.nom, 'niveau': classe.niveau} for classe in classes])
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des classes: {e}")
        return jsonify({"message": "Erreur interne"}), 500

# GET /classes/{id}
@app.route('/classes/<int:id>', methods=['GET'])
def get_classe(id):
    try:
        classe = db.session.get(Classe, id)
        if not classe:
            logger.warning(f"Classe avec ID {id} non trouvée")
            return jsonify({'message': 'Classe non trouvée'}), 404
        logger.info(f"Classe récupérée : {classe.nom} (ID: {id})")
        return jsonify({'id': classe.id, 'nom': classe.nom, 'niveau': classe.niveau})
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la classe {id}: {e}")
        return jsonify({"message": "Erreur interne"}), 500

# POST /classes
@app.route('/classes', methods=['POST'])
def add_classe():
    data = request.get_json()
    if not data or "nom" not in data or "niveau" not in data:
        logger.warning("Requête invalide reçue pour l'ajout d'une classe")
        return jsonify({"message": "Données invalides"}), 400

    try:
        new_class = Classe(nom=data['nom'], niveau=data['niveau'])
        db.session.add(new_class)
        db.session.commit()
        logger.info(f"Classe ajoutée : {data['nom']} (Niveau: {data['niveau']})")
        return jsonify({"message": "Classe ajoutée"}), 201
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de la classe {data.get('nom')}: {e}")
        db.session.rollback()
        return jsonify({"message": "Erreur lors de l'ajout"}), 500

# DELETE /classes/{id}
@app.route('/classes/<int:id>', methods=['DELETE'])
def delete_classe(id):
    try:
        classe = db.session.get(Classe, id)
        if not classe:
            logger.warning(f"Tentative de suppression d'une classe inexistante (ID: {id})")
            return jsonify({'message': 'Classe non trouvée'}), 404

        db.session.delete(classe)
        db.session.commit()
        logger.info(f"Classe supprimée : {classe.nom} (ID: {id})")
        return jsonify({'message': 'Classe supprimée avec succès'})
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la classe {id}: {e}")
        db.session.rollback()
        return jsonify({"message": "Erreur lors de la suppression"}), 500

# === Configuration de Swagger UI ===
SWAGGER_URL = "/docs"
API_URL = "/swagger.yml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "API de gestion des classes"}
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
    app.run(host='0.0.0.0', port=5001)

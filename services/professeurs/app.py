from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import requests
import os
from services.logging_config import setup_logging
import logging
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# === Configuration des logs ===
# Initialisation du logging
setup_logging()
logger = logging.getLogger("ProfesseursService")


# === Configuration de la base de données ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Redington@db_professeurs:5432/professeurs_db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Pour tester en local
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# === Modèles de données ===
class Professeur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    specialite = db.Column(db.String(100), nullable=True)

class ProfesseurCours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professeur_id = db.Column(db.Integer, nullable=False)
    cours_id = db.Column(db.Integer, nullable=False)

# === Routes ===

@app.route('/professeurs', methods=['GET'])
def get_professeurs():
    """ Obtenir la liste des professeurs avec leur nom et spécialité. """
    try:
        professeurs = Professeur.query.all()
        profs_list = [{"id": prof.id, "nom": prof.nom, "specialite": prof.specialite} for prof in professeurs]

        logger.info("Liste des professeurs récupérée avec succès")
        return jsonify(profs_list), 200

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des professeurs : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/professeurs', methods=['POST'])
def add_professeur():
    """ Ajouter un professeur. """
    try:
        data = request.get_json()

        # Vérification des champs requis
        if not data or "nom" not in data or not data["nom"].strip():
            logger.warning("Données manquantes ou nom vide pour l'ajout d'un professeur")
            return jsonify({"message": "Le champ 'nom' est requis"}), 400

        new_prof = Professeur(
            nom=data['nom'].strip(),
            specialite=data.get('specialite', "").strip() or None  # Null si spécialité vide
        )
        db.session.add(new_prof)
        db.session.commit()

        logger.info(f"Professeur ajouté : {new_prof.nom} (ID: {new_prof.id})")
        return jsonify({
            "message": "Professeur ajouté avec succès",
            "id": new_prof.id
        }), 201

    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du professeur : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500


@app.route('/professeurs/<int:prof_id>/cours/<int:cours_id>', methods=['POST'])
def assign_cours(prof_id, cours_id):
    """ Assigner un cours à un professeur. """
    try:
        professeur = Professeur.query.get(prof_id)
        if not professeur:
            logger.warning(f"Professeur ID {prof_id} introuvable")
            return jsonify({"message": "Professeur introuvable"}), 404

        try:
            response = requests.get(f"http://microservice_cours:5002/cours/{cours_id}")
            if response.status_code != 200:
                logger.warning(f"Cours ID {cours_id} introuvable")
                response.raise_for_status()  # Lève une exception si le statut HTTP est une erreur
                return jsonify({"message": "Cours introuvable"}), 404
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de communication avec le microservice cours : {str(e)}")
            return jsonify({"message": "Erreur lors de la communication avec le microservice cours"}), 502

        professeur_cours = ProfesseurCours(professeur_id=prof_id, cours_id=cours_id)
        db.session.add(professeur_cours)
        db.session.commit()

        logger.info(f"Cours {cours_id} assigné au professeur {prof_id}")
        return jsonify({"message": "Cours assigné au professeur"}), 200

    except Exception as e:
        logger.error(f"Erreur lors de l'assignation du cours : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/professeurs/<int:prof_id>/cours', methods=['GET'])
def get_professeur_cours(prof_id):
    """ Récupérer la liste des cours d'un professeur. """
    try:
        professeur = Professeur.query.get(prof_id)
        if not professeur:
            logger.warning(f"Professeur ID {prof_id} introuvable")
            return jsonify({"message": "Professeur introuvable"}), 404

        cours_list = []
        for pc in ProfesseurCours.query.filter_by(professeur_id=prof_id).all():
            try:
                response = requests.get(f"http://microservice_cours:5002/cours/{pc.cours_id}")
                if response.status_code == 200:
                    cours_list.append(response.json())
                else:
                    logger.warning(f"Cours ID {pc.cours_id} introuvable")
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur de communication avec le microservice cours : {str(e)}")
                return jsonify({"message": "Erreur lors de la récupération des cours"}), 502

        logger.info(f"Liste des cours du professeur {prof_id} récupérée avec succès")
        return jsonify({"professeur": professeur.nom, "cours": cours_list})

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des cours du professeur : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500
    
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

# === Lancer l'application ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)

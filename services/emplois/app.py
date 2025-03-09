from flask import Flask, request, jsonify, send_file
import os
from flask_sqlalchemy import SQLAlchemy
import requests
import logging
from logging_config import setup_logging
from datetime import datetime
from sqlalchemy import and_
from flask_swagger_ui import get_swaggerui_blueprint
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# === Configuration des logs ===
# Initialisation du logging
setup_logging()
logger = logging.getLogger("EmploisDuTempsService")

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Redington@db_emplois:5432/emplois_db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# === Configuration de Swagger UI ===
SWAGGER_URL = "/docs"
API_URL = "/swagger.yml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "API Emplois du Temps"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/swagger.yml")
def swagger_file():
    return send_file(os.path.join(os.getcwd(), "swagger.yml"))

# Modèle de la base de données
class EmploiDuTemps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classe_id = db.Column(db.Integer, nullable=False)
    cours_id = db.Column(db.Integer, nullable=False)
    professeur_id = db.Column(db.Integer, nullable=False)
    jour = db.Column(db.String(20), nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)  
    heure_fin = db.Column(db.Time, nullable=False)

# Création des tables si nécessaire
with app.app_context():
    db.create_all()

@app.route('/emplois_du_temps', methods=['POST'])
def add_emploi():
    try:
        data = request.json
        required_fields = ['classe_id', 'cours_id', 'professeur_id', 'jour', 'heure_debut', 'heure_fin']
        if not all(field in data for field in required_fields):
            logger.warning("Tentative d'ajout avec des champs manquants.")
            return jsonify({"error": "Champs requis : classe_id, cours_id, professeur_id, jour, heure_debut, heure_fin"}), 400
        
        # Vérification des micro-services
        services = {
            "classe": f"http://microservice_classes/classes/{data['classe_id']}",
            "cours": f"http://microservice_cours:5002/cours/{data['cours_id']}",
            "professeur": f"http://microservice_professeurs:5004/professeurs/{data['professeur_id']}"
        }

        for key, url in services.items():
            response = requests.get(url)
            if response.status_code != 200:
                logger.warning(f"Échec de la vérification du service {key} ({url})")
                return jsonify({"error": f"{key.capitalize()} introuvable"}), 404

        # Conversion des horaires
        try:
            heure_debut = datetime.strptime(data['heure_debut'], "%H:%M").time()
            heure_fin = datetime.strptime(data['heure_fin'], "%H:%M").time()
        except ValueError:
            logger.warning("Format d'heure invalide fourni.")
            return jsonify({"error": "Format d'heure invalide, utilisez HH:MM"}), 400

        # Vérification des conflits
        conflit = EmploiDuTemps.query.filter(
            EmploiDuTemps.professeur_id == data['professeur_id'],
            EmploiDuTemps.jour == data['jour'],
            and_(
                EmploiDuTemps.heure_debut < heure_fin,
                EmploiDuTemps.heure_fin > heure_debut
            )
        ).first()

        if conflit:
            logger.warning(f"Conflit détecté pour professeur {data['professeur_id']} à {data['heure_debut']} - {data['heure_fin']}.")
            return jsonify({"error": "Conflit d'emploi du temps"}), 409

        # Remove heure_debut and heure_fin from the data dictionary
        data.pop('heure_debut')
        data.pop('heure_fin')

        # Create new EmploiDuTemps instance
        new_emploi = EmploiDuTemps(**data, heure_debut=heure_debut, heure_fin=heure_fin)
        db.session.add(new_emploi)
        db.session.commit()

        logger.info(f"Emploi du temps ajouté : {data}")
        return jsonify({"message": "Emploi du temps ajouté avec succès"}), 201

    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de l'emploi du temps : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500


@app.route('/emplois_du_temps', methods=['GET'])
def get_emplois():
    try:
        emplois = EmploiDuTemps.query.all()
        emplois_list = [{
            "id": emploi.id,
            "classe_id": emploi.classe_id,
            "cours_id": emploi.cours_id,
            "professeur_id": emploi.professeur_id,
            "jour": emploi.jour,
            "heure_debut": emploi.heure_debut.strftime("%H:%M"),
            "heure_fin": emploi.heure_fin.strftime("%H:%M")
        } for emploi in emplois]

        logger.info("Récupération de tous les emplois du temps.")
        return jsonify(emplois_list)
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des emplois du temps : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/emplois_du_temps/<int:id>', methods=['PUT'])
def update_emploi(id):
    try:
        emploi = EmploiDuTemps.query.get(id)
        if not emploi:
            logger.warning(f"Tentative de mise à jour d'un emploi du temps inexistant (ID {id}).")
            return jsonify({"message": "Emploi du temps introuvable"}), 404
        
        data = request.json
        for key, value in data.items():
            if key in ["heure_debut", "heure_fin"]:
                value = datetime.strptime(value, "%H:%M").time()
            setattr(emploi, key, value)

        db.session.commit()
        logger.info(f"Emploi du temps {id} mis à jour : {data}")
        return jsonify({"message": "Emploi du temps mis à jour avec succès"})
    
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'emploi du temps {id} : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/emplois_du_temps/<int:id>', methods=['DELETE'])
def delete_emploi(id):
    try:
        emploi = EmploiDuTemps.query.get(id)
        if not emploi:
            logger.warning(f"Tentative de suppression d'un emploi du temps inexistant (ID {id}).")
            return jsonify({"message": "Emploi du temps introuvable"}), 404
        
        db.session.delete(emploi)
        db.session.commit()
        logger.info(f"Emploi du temps {id} supprimé")
        return jsonify({"message": "Emploi du temps supprimé avec succès"})
    
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'emploi du temps {id} : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)

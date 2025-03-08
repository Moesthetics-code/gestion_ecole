from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from services.logging_config import setup_logging
import logging
import requests
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# === Configuration des logs ===
# Initialisation du logging
setup_logging()
logger = logging.getLogger("EtudiantsService")

# === Configuration de la base de données ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Redington@db_etudiants:5432/etudiants_db'
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Utiliser SQLite en mémoire pour tester en local
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    classe_id = db.Column(db.Integer, nullable=False)

# === Routes ===

@app.route('/etudiants', methods=['GET'])
def get_etudiants():
    """ Récupérer tous les étudiants. """
    try:
        etudiants = Etudiant.query.all()
        logger.info(f"{len(etudiants)} étudiants récupérés avec succès")  # 🔍 Ajout du log
        return jsonify([{"id": e.id, "nom": e.nom, "classe_id": e.classe_id} for e in etudiants])
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des étudiants : {str(e)}")
        return jsonify({"message": "Erreur interne du serveur"}), 500

@app.route('/etudiants', methods=['POST'])
def add_etudiant():
    """ Ajouter un étudiant. """
    try:
        data = request.json  # 📌 Récupérer les données d'abord

        # Vérifier la présence des champs requis
        if not data or "nom" not in data or "classe_id" not in data:
            logger.warning("Données manquantes pour l'ajout d'un étudiant")
            return jsonify({"message": "Champs 'nom' et 'classe_id' requis"}), 400

        # Vérifier si la classe existe en envoyant une requête au microservice des classes
        response = requests.get(f"http://microservice_classes:5001/classes/{data['classe_id']}")

        if response.status_code != 200:
            logger.warning(f"Classe ID {data['classe_id']} introuvable")
            return jsonify({"message": "Classe non trouvée"}), 404

        # Création de l'étudiant
        new_etudiant = Etudiant(nom=data['nom'], classe_id=data['classe_id'])
        db.session.add(new_etudiant)
        db.session.commit()

        logger.info(f"Étudiant {data['nom']} ajouté avec succès (ID: {new_etudiant.id})")
        return jsonify({"message": "Étudiant ajouté"}), 201

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de communication avec le microservice classe : {str(e)}")
        return jsonify({"message": "Erreur lors de la communication avec le microservice classe"}), 502

    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de l'étudiant : {str(e)}")
        return jsonify({"message": "Erreur interne du serveur"}), 500

# === Lancer l'application ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)

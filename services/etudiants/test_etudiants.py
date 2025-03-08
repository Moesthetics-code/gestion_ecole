import pytest
from flask import json
from .app import app, db, Etudiant
from unittest.mock import patch
import os

@pytest.fixture
def client():
    """Fixture pour configurer un client de test Flask"""
    app.config["TESTING"] = True
    db_url = os.getenv("TEST_COURS_DB_URL", "sqlite:///:memory:")  # Utiliser PostgreSQL si disponible
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Créer toutes les tables nécessaires
        yield client
        with app.app_context():
            db.drop_all()  # Nettoyer après les tests

def test_get_etudiants_vide(client):
    """Tester la récupération d'une liste vide d'étudiants"""
    response = client.get("/etudiants")
    assert response.status_code == 200
    assert response.json == []


def test_add_etudiant_succes(client):
    """Tester l'ajout d'un étudiant avec succès"""
    # Simuler la réponse du microservice de classe
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200  # La classe existe

        data = {"nom": "Alice", "classe_id": 1}
        response = client.post("/etudiants", json=data)

        assert response.status_code == 201
        assert response.json["message"] == "Étudiant ajouté"

        # Vérifier si l'étudiant est bien ajouté dans la base de données
        with app.app_context():
            etudiant = Etudiant.query.filter_by(nom="Alice").first()
            assert etudiant is not None
            assert etudiant.classe_id == 1


def test_add_etudiant_classe_inexistante(client):
    """Tester l'ajout d'un étudiant avec une classe inexistante"""
    # Simuler une classe inexistante
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 404

        data = {"nom": "Bob", "classe_id": 99}
        response = client.post("/etudiants", json=data)

        assert response.status_code == 404
        assert response.json["message"] == "Classe non trouvée"

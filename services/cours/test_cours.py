import pytest
from flask import json
from unittest.mock import patch
from .app import app, db, Cours
import os

@pytest.fixture
def client():
    """Fixture pour configurer un client de test Flask"""
    app.config["TESTING"] = True
    db_url = os.getenv("TEST_COURS_DB_URL", "sqlite:///:memory:")  # Utiliser PostgreSQL si disponible
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Créer toutes les tables
        yield client
        with app.app_context():
            db.drop_all()

# Test pour récupérer tous les cours
def test_get_all_cours(client):
    """Tester la récupération de tous les cours"""
    cours1 = Cours(nom="Mathématiques", classe_id=1)
    cours2 = Cours(nom="Physique", classe_id=1)
    with app.app_context():
        db.session.add(cours1)
        db.session.add(cours2)
        db.session.commit()

    response = client.get("/cours")
    assert response.status_code == 200
    assert len(response.json) == 2  # Nous avons ajouté 2 cours
    assert response.json[0]["nom"] == "Mathématiques"
    assert response.json[1]["nom"] == "Physique"

# Test pour ajouter un cours avec une classe valide
def test_add_cours_valid_classe(client):
    """Tester l'ajout d'un cours avec une classe valide"""
    data = {"nom": "Mathématiques", "classe_id": 1}
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200  # Simuler une classe valide

        response = client.post("/cours", json=data)
        assert response.status_code == 201
        assert response.json["message"] == "Cours ajouté"

# Test pour ajouter un cours avec une classe inexistante
def test_add_cours_invalid_classe(client):
    """Tester l'ajout d'un cours avec une classe inexistante"""
    data = {"nom": "Mathématiques", "classe_id": 99}
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 404  # Simuler une classe inexistante

        response = client.post("/cours", json=data)
        assert response.status_code == 400
        assert response.json["message"] == "Classe introuvable"

# Test pour mettre à jour un cours
def test_update_cours(client):
    """Tester la mise à jour d'un cours"""
    cours = Cours(nom="Mathématiques", classe_id=1)
    with app.app_context():
        db.session.add(cours)
        db.session.commit()
        cours_id = cours.id  # 🔹 Récupérer l'ID avant fermeture

    data = {"nom": "Mathématiques Avancées", "classe_id": 1}
    response = client.put(f"/cours/{cours_id}", json=data)
    
    assert response.status_code == 200
    with app.app_context():
        updated_cours = Cours.query.get(cours.id)
        assert updated_cours.nom == "Mathématiques Avancées"

# Test pour supprimer un cours
def test_delete_cours(client):
    """Tester la suppression d'un cours"""
    cours = Cours(nom="Mathématiques", classe_id=1)
    with app.app_context():
        db.session.add(cours)
        db.session.commit()
        cours_id = cours.id  # 🔹 Récupérer l'ID avant fermeture

    response = client.delete(f"/cours/{cours_id}")
    
    assert response.status_code == 200
    with app.app_context():
        deleted_cours = Cours.query.get(cours.id)
        assert deleted_cours is None

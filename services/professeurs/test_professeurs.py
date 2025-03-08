import pytest
from .app import app, db, Professeur, ProfesseurCours
from unittest.mock import patch
import os

@pytest.fixture
def client():
    """Créer une instance de test de l'application Flask."""
    app.config['TESTING'] = True
    db_url = os.getenv("TEST_COURS_DB_URL", "sqlite:///:memory:")  # Utiliser PostgreSQL si disponible
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_add_professeur(client):
    """Test de l'ajout d'un professeur."""
    response = client.post('/professeurs', json={"nom": "Jean Dupont", "specialite": "Maths"})
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["message"] == "Professeur ajouté avec succès"
    assert "id" in json_data

def test_add_professeur_missing_name(client):
    """Test d'ajout de professeur avec un champ manquant."""
    response = client.post('/professeurs', json={"specialite": "Physique"})
    
    assert response.status_code == 400  # Le code 400 est plus approprié ici
    json_data = response.get_json()
    assert "message" in json_data
    assert json_data["message"] == "Champ 'nom' requis"

def test_assign_cours_professeur_not_found(client):
    """Test d'assignation d'un cours à un professeur inexistant."""
    response = client.post('/professeurs/1/cours/101')
    
    assert response.status_code == 404
    assert response.get_json()["message"] == "Professeur introuvable"

@patch("requests.get")
def test_assign_cours(mock_get, client):
    """Test d'assignation d'un cours à un professeur existant."""
    # Ajouter un professeur en base
    with app.app_context():
        prof = Professeur(nom="Alice Martin", specialite="Informatique")
        db.session.add(prof)
        db.session.commit()
    
    # Simuler une réponse du microservice cours
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 101, "nom": "Algèbre"}
    
    response = client.post('/professeurs/1/cours/101')
    
    assert response.status_code == 200
    assert response.get_json()["message"] == "Cours assigné au professeur"

@patch("requests.get")
def test_get_professeur_cours(mock_get, client):
    """Test de récupération des cours d'un professeur existant."""
    # Ajouter un professeur en base
    with app.app_context():
        prof = Professeur(nom="Alice Martin", specialite="Informatique")
        db.session.add(prof)
        db.session.commit()

        # Ajouter un cours pour ce professeur
        prof_cours = ProfesseurCours(professeur_id=prof.id, cours_id=101)
        db.session.add(prof_cours)
        db.session.commit()

    # Simuler la réponse du microservice des cours
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 101, "nom": "Algèbre"}

    # Effectuer la requête
    response = client.get('/professeurs/1/cours')

    # Vérifications
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["professeur"] == "Alice Martin"
    assert len(json_data["cours"]) == 1  # Vérifier qu'un cours est bien assigné
    assert json_data["cours"][0]["nom"] == "Algèbre"  # Vérifier le nom du cours

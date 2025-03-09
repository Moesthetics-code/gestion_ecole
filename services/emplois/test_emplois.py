import pytest
import requests_mock
from .app import app, db, EmploiDuTemps
from datetime import datetime
import os

@pytest.fixture
def client():
    app.config["TESTING"] = True
    db_url = os.getenv("TEST_COURS_DB_URL", "sqlite:///:memory:")  # Utiliser PostgreSQL si disponible
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    with app.app_context():
        db.create_all()
    client = app.test_client()
    yield client
    # Clean up the test database after each test
    with app.app_context():
        db.drop_all()

def test_add_emploi(client):
    with requests_mock.Mocker() as m:
        m.get("http://microservice_classes/classes/1", json={"id": 1, "nom": "Classe 1"})
        m.get("http://microservice_cours:5002/cours/1", json={"id": 1, "nom": "Maths"})
        m.get("http://microservice_professeurs:5004/professeurs/1", json={"id": 1, "nom": "Mr. Smith"})
        
        response = client.post("/emplois_du_temps", json={
            "classe_id": 1,
            "cours_id": 1,
            "professeur_id": 1,
            "jour": "Lundi",
            "heure_debut": "08:00",
            "heure_fin": "10:00"
        })
        assert response.status_code == 201
        assert response.json["message"] == "Emploi du temps ajouté avec succès"

def test_get_emplois(client):
    emploi = EmploiDuTemps(classe_id=1, cours_id=1, professeur_id=1, jour="Lundi",
                           heure_debut=datetime.strptime("08:00", "%H:%M").time(),
                           heure_fin=datetime.strptime("10:00", "%H:%M").time())
    with app.app_context():
        db.session.add(emploi)
        db.session.commit()

    with requests_mock.Mocker() as m:
        m.get("http://microservice_classes:5001/classes/1", json={"id": 1, "nom": "Classe 1"})
        m.get("http://microservice_cours:5002/cours/1", json={"id": 1, "nom": "Maths"})
        m.get("http://microservice_professeurs:5004/professeurs/1", json={"id": 1, "nom": "Mr. Smith"})

        response = client.get("/emplois_du_temps")
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["classe_id"] == 1
        assert response.json[0]["cours_id"] == 1
        assert response.json[0]["professeur_id"] == 1
        assert response.json[0]["jour"] == "Lundi"
        assert response.json[0]["heure_debut"] == "08:00"
        assert response.json[0]["heure_fin"] == "10:00"

def test_update_emploi(client):
    emploi = EmploiDuTemps(classe_id=1, cours_id=1, professeur_id=1, jour="Lundi",
                           heure_debut=datetime.strptime("08:00", "%H:%M").time(),
                           heure_fin=datetime.strptime("10:00", "%H:%M").time())
    with app.app_context():
        db.session.add(emploi)
        db.session.commit()  # Commit the session to persist the instance
        
        # Refetch the emploi from the session to make sure it is attached
        emploi = EmploiDuTemps.query.get(emploi.id)
        
        # Now perform the update request
        response = client.put(f"/emplois_du_temps/{emploi.id}", json={"jour": "Mardi"})
        assert response.status_code == 200
        assert response.json["message"] == "Emploi du temps mis à jour avec succès"

def test_delete_emploi(client):
    with app.app_context():
        emploi = EmploiDuTemps(classe_id=1, cours_id=1, professeur_id=1, jour="Lundi",
                               heure_debut=datetime.strptime("08:00", "%H:%M").time(),
                               heure_fin=datetime.strptime("10:00", "%H:%M").time())
        db.session.add(emploi)
        db.session.commit()

        # Recharger l'instance pour éviter l'erreur DetachedInstanceError
        emploi = db.session.get(EmploiDuTemps, emploi.id)

        response = client.delete(f"/emplois_du_temps/{emploi.id}")
    
    assert response.status_code == 200
    assert response.json["message"] == "Emploi du temps supprimé avec succès"

import pytest
from .app import app, db, Classe
import os

@pytest.fixture
def client():
    """Client de test avec application Flask et base de données PostgreSQL."""
    app.config['TESTING'] = True
    db_url = os.getenv("TEST_CLASSES_DB_URL", "sqlite:///:memory:")  # Utiliser PostgreSQL si disponible
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    
    with app.app_context():
        db.create_all()
    
    yield app.test_client()

    with app.app_context():
        db.session.remove()
        db.drop_all()

# Test GET /classes
def test_get_classes(client):
    with app.app_context():
        classe = Classe(nom='Mathématiques', niveau='L1')
        db.session.add(classe)
        db.session.commit()

    response = client.get('/classes')
    assert response.status_code == 200

    json_data = response.get_json()
    assert len(json_data) == 1
    assert json_data[0]['nom'] == 'Mathématiques'
    assert json_data[0]['niveau'] == 'L1'

# Test GET /classes/{id}
def test_get_classe_by_id(client):
    with app.app_context():
        classe = Classe(nom='Mathématiques', niveau='L1')
        db.session.add(classe)
        db.session.commit()
        classe_id = classe.id

    response = client.get(f'/classes/{classe_id}')
    assert response.status_code == 200

    json_data = response.get_json()
    assert json_data['nom'] == 'Mathématiques'
    assert json_data['niveau'] == 'L1'

# Test POST /classes
def test_add_classe(client):
    data = {'nom': 'Informatique', 'niveau': 'L2'}
    response = client.post('/classes', json=data)
    assert response.status_code == 201

    with app.app_context():
        classe = Classe.query.filter_by(nom='Informatique').first()
        assert classe is not None
        assert classe.nom == 'Informatique'
        assert classe.niveau == 'L2'

# Test DELETE /classes/{id}
def test_delete_classe(client):
    with app.app_context():
        classe = Classe(nom='Informatique', niveau='L2')
        db.session.add(classe)
        db.session.commit()
        classe_id = classe.id

    response = client.delete(f'/classes/{classe_id}')
    assert response.status_code == 200

    response = client.get(f'/classes/{classe_id}')
    assert response.status_code == 404  # La classe ne doit plus exister

    response = client.delete(f'/classes/{classe_id}')
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['message'] == 'Classe non trouvée'

# Test GET /classes/{id} pour une classe inexistante
def test_get_classe_not_found(client):
    response = client.get('/classes/999')
    assert response.status_code == 404

    json_data = response.get_json()
    assert json_data is not None
    assert json_data['message'] == 'Classe non trouvée'

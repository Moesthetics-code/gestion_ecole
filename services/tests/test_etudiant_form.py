import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Fixture pour configurer le WebDriver avec l'URL du conteneur Selenium
@pytest.fixture
def driver():
    # Connexion au serveur Selenium exposé sur le port 4444 dans Docker
    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',  # URL de Selenium dans le conteneur Docker
        desired_capabilities={'browserName': 'chrome'}
    )
    driver.get("http://localhost:5000/etudiant-form")  # Remplacez par l'URL correcte de votre application dans le conteneur
    yield driver
    driver.quit()

# Test pour ajouter un étudiant
def test_add_etudiant(driver):
    # Interaction avec les éléments de la page
    driver.find_element(By.NAME, "nom").send_keys("Jean Dupont")
    
    # Sélectionner la première option dans le select
    select = driver.find_element(By.NAME, "classe_id")
    select.send_keys(Keys.DOWN)  # Sélectionner la première option
    select.send_keys(Keys.ENTER)
    
    driver.find_element(By.TAG_NAME, "button").click()
    
    # Laissez le backend traiter la requête
    time.sleep(2)

    # Vérifiez que l'étudiant a bien été ajouté
    assert "Jean Dupont" in driver.page_source

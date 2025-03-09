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
    driver.get("http://localhost:5000/classe-form")  # Remplacez par l'URL correcte de votre application dans le conteneur
    yield driver
    driver.quit()

# Test pour ajouter une classe
def test_add_class(driver):
    # Interaction avec les éléments de la page
    driver.find_element(By.NAME, "nom").send_keys("Mathématiques")
    driver.find_element(By.NAME, "niveau").send_keys("L1")
    driver.find_element(By.TAG_NAME, "button").click()
    
    # Laissez le backend traiter la requête (on peut aussi remplacer le time.sleep par un wait explicite)
    time.sleep(2)  

    # Assertions pour vérifier que les informations sont présentes sur la page
    assert "Mathématiques" in driver.page_source
    assert "L1" in driver.page_source

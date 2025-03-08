import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

@pytest.fixture
def driver():
    driver = webdriver.Chrome()  # Assurez-vous que chromedriver est installé
    driver.get("http://localhost:3000")  # Remplacez par l'URL correcte
    yield driver
    driver.quit()

def test_add_class(driver):
    driver.find_element(By.NAME, "nom").send_keys("Mathématiques")
    driver.find_element(By.NAME, "niveau").send_keys("L1")
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(2)  # Laissez le backend traiter la requête

    assert "Mathématiques" in driver.page_source
    assert "L1" in driver.page_source

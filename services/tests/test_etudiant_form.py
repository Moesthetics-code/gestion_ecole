import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.get("http://localhost:3000")  # Remplacez par l'URL correcte
    yield driver
    driver.quit()

def test_add_etudiant(driver):
    driver.find_element(By.NAME, "nom").send_keys("Jean Dupont")
    select = driver.find_element(By.NAME, "classe_id")
    select.send_keys(Keys.DOWN)
    select.send_keys(Keys.ENTER)
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(2)

    assert "Jean Dupont" in driver.page_source

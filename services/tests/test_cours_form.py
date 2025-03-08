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

def test_add_cours(driver):
    driver.find_element(By.NAME, "nom").send_keys("Algèbre")
    select = driver.find_element(By.NAME, "classe_id")
    select.send_keys(Keys.DOWN)  # Sélectionnez la première option
    select.send_keys(Keys.ENTER)
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(2)

    assert "Algèbre" in driver.page_source

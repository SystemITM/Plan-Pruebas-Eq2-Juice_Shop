from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import os


def before_scenario(context, scenario):
    """
    Se ejecuta antes de cada escenario.
    Prepara el navegador y define la URL base del SUT.
    """

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    context.driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    context.wait = WebDriverWait(context.driver, 20)

    # URL local de OWASP Juice Shop
    context.base_url = os.getenv("BASE_URL", "http://localhost:3000/").rstrip("/")


def after_scenario(context, scenario):
    """
    Se ejecuta después de cada escenario.
    Cierra el navegador para dejar cada prueba independiente.
    """

    if hasattr(context, "driver"):
        context.driver.quit()
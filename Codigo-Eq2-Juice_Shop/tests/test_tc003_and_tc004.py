import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "http://localhost:3000"

EMAIL_VALIDO = "test@test.com"
PASSWORD_VALIDO = "Prueba123!"
PASSWORD_INVALIDO = "ClaveMala123"


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--start-maximized")

    navegador = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    yield navegador
    navegador.quit()


def safe_click(driver, by, locator, timeout=4):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )
        driver.execute_script("arguments[0].click();", element)
    except Exception:
        pass


def cerrar_banners(driver):
    safe_click(driver, By.CSS_SELECTOR, "button[aria-label='Close Welcome Banner']")
    safe_click(driver, By.CSS_SELECTOR, "a[aria-label='dismiss cookie message']")
    safe_click(driver, By.CSS_SELECTOR, "button[aria-label='dismiss cookie message']")
    safe_click(driver, By.XPATH, "//button[contains(., 'Me want it!')]")


def abrir_login(driver):
    driver.get(f"{BASE_URL}/#/login")
    cerrar_banners(driver)


def diligenciar_login(driver, email, password):
    wait = WebDriverWait(driver, 15)

    campo_email = wait.until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    campo_email.clear()
    campo_email.send_keys(email)

    campo_password = wait.until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    campo_password.clear()
    campo_password.send_keys(password)


def hacer_click_login(driver):
    wait = WebDriverWait(driver, 15)

    boton_login = wait.until(
        EC.element_to_be_clickable((By.ID, "loginButton"))
    )

    driver.execute_script("arguments[0].click();", boton_login)


def test_tc003_login_con_credenciales_validas(driver):
    """
    TC-003
    Inicio de sesión con credenciales válidas.
    """

    # =========================
    # ARRANGE
    # =========================
    abrir_login(driver)

    # =========================
    # ACT
    # =========================
    diligenciar_login(driver, EMAIL_VALIDO, PASSWORD_VALIDO)
    hacer_click_login(driver)

    # =========================
    # ASSERT
    # =========================
    wait = WebDriverWait(driver, 15)

    wait.until(
        lambda d: "/search" in d.current_url or len(d.find_elements(By.ID, "navbarYourBasket")) > 0
    )

    assert "/search" in driver.current_url or driver.find_elements(By.ID, "navbarYourBasket"), (
        "El sistema no inició sesión correctamente con credenciales válidas."
    )

    print("[SUCCESS] TC-003 COMPLETADO: Login exitoso con credenciales válidas.")


def test_tc004_login_con_contrasena_incorrecta(driver):
    """
    TC-004
    Inicio de sesión con contraseña incorrecta.
    """

    # =========================
    # ARRANGE
    # =========================
    abrir_login(driver)

    # =========================
    # ACT
    # =========================
    diligenciar_login(driver, EMAIL_VALIDO, PASSWORD_INVALIDO)
    hacer_click_login(driver)

    # =========================
    # ASSERT
    # =========================
    wait = WebDriverWait(driver, 15)

    try:
        mensaje_error = wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(normalize-space(), 'Invalid email or password')]"
            ))
        ).text
    except TimeoutException:
        try:
            mensaje_error = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".error"))
            ).text
        except TimeoutException:
            mensaje_error = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "simple-snack-bar"))
            ).text

    assert "Invalid email or password" in mensaje_error, (
        f"No apareció el mensaje esperado de credenciales inválidas. Mensaje recibido: {mensaje_error}"
    )

    assert "/login" in driver.current_url, (
        "El sistema no debería permitir salir del login con contraseña incorrecta."
    )

    print("[SUCCESS] TC-004 COMPLETADO: Login rechazado correctamente con contraseña incorrecta.")
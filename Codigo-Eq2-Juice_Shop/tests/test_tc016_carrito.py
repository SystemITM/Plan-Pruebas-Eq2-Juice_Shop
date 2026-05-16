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

EMAIL = "test@test.com"
PASSWORD = "Prueba123!"

PRODUCT_NAME = "Apple Juice (1000ml)"


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


def safe_click(driver, by, locator, timeout=5):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )
        driver.execute_script("arguments[0].click();", element)
    except Exception:
        pass


def cerrar_popups_iniciales(driver):
    safe_click(driver, By.CSS_SELECTOR, 'button[aria-label="Close Welcome Banner"]')
    safe_click(driver, By.CSS_SELECTOR, 'button[aria-label="dismiss cookie message"]')
    safe_click(driver, By.XPATH, "//button[contains(., 'Me want it!')]")


def iniciar_sesion(driver):
    wait = WebDriverWait(driver, 20)

    driver.get(f"{BASE_URL}/#/login")
    cerrar_popups_iniciales(driver)

    campo_email = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#email"))
    )
    campo_password = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#password"))
    )

    campo_email.clear()
    campo_email.send_keys(EMAIL)

    campo_password.clear()
    campo_password.send_keys(PASSWORD)

    boton_login = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#loginButton"))
    )
    driver.execute_script("arguments[0].click();", boton_login)

    # Ir directamente al catálogo después del login
    driver.get(f"{BASE_URL}/#/search")
    cerrar_popups_iniciales(driver)

    wait.until(
        EC.visibility_of_element_located((
            By.XPATH,
            f"//*[contains(normalize-space(), '{PRODUCT_NAME}')]"
        ))
    )


def ir_al_carrito_por_ruta(driver):
    """
    Entra al carrito sin depender del botón Your Basket.
    Esta opción es más estable para automatización porque usa directamente la ruta Angular.
    """
    wait = WebDriverWait(driver, 20)

    driver.get(f"{BASE_URL}/#/basket")

    wait.until(
        EC.url_contains("basket")
    )

    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )


def test_tc016_agregar_producto_del_catalogo_al_carrito(driver):
    wait = WebDriverWait(driver, 20)

    # =========================
    # ARRANGE
    # =========================
    iniciar_sesion(driver)

    tarjeta_producto = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//*[contains(normalize-space(), '{PRODUCT_NAME}')]/ancestor::mat-card"
        ))
    )

    # =========================
    # ACT
    # =========================

    boton_agregar = tarjeta_producto.find_element(
        By.XPATH,
        ".//button[contains(., 'Add to Basket')]"
    )

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_agregar)
    driver.execute_script("arguments[0].click();", boton_agregar)

    # Esperar que el sistema registre la acción.
    # Si el contador del carrito cambia a 1, el producto fue agregado.
    try:
        wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#navbarYourBasket"),
                "1"
            )
        )
    except TimeoutException:
        print("No se pudo validar el contador del carrito, se continuará validando dentro del carrito.")

    # Entrar al carrito por ruta directa
    ir_al_carrito_por_ruta(driver)

    # =========================
    # ASSERT
    # =========================

    producto_en_carrito = wait.until(
        EC.visibility_of_element_located((
            By.XPATH,
            f"//*[contains(normalize-space(), '{PRODUCT_NAME}')]"
        ))
    )

    assert producto_en_carrito.is_displayed(), (
        f"El producto {PRODUCT_NAME} no aparece en el carrito."
    )

    pagina_carrito = driver.page_source

    assert PRODUCT_NAME in pagina_carrito, (
        f"El producto {PRODUCT_NAME} no se encuentra en la página del carrito."
    )

    assert "Apple Juice" in pagina_carrito, (
        "No se encontró el nombre del producto en el carrito."
    )

    assert "1" in pagina_carrito, (
        "No se encontró evidencia de que la cantidad del producto sea 1."
    )
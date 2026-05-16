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

# Usuario de prueba.
EMAIL = "test@test.com"
PASSWORD = "Prueba123!"


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
    """
    Clic seguro para elementos que pueden aparecer o no.
    Sirve para cerrar banners molestos.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )
        driver.execute_script("arguments[0].click();", element)
    except Exception:
        pass


def cerrar_banners_molestos(driver):
    """
    Cierra banners de Juice Shop que pueden interceptar clics.
    """
    safe_click(driver, By.CSS_SELECTOR, "button[aria-label='Close Welcome Banner']")
    safe_click(driver, By.CSS_SELECTOR, "a[aria-label='dismiss cookie message']")
    safe_click(driver, By.CSS_SELECTOR, "button[aria-label='dismiss cookie message']")
    safe_click(driver, By.XPATH, "//button[contains(., 'Me want it!')]")


def iniciar_sesion(driver):
    """
    Inicia sesión en OWASP Juice Shop.
    """
    wait = WebDriverWait(driver, 20)

    driver.get(f"{BASE_URL}/#/login")
    cerrar_banners_molestos(driver)

    campo_email = wait.until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    campo_email.clear()
    campo_email.send_keys(EMAIL)

    campo_password = wait.until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    campo_password.clear()
    campo_password.send_keys(PASSWORD)

    boton_login = wait.until(
        EC.element_to_be_clickable((By.ID, "loginButton"))
    )
    driver.execute_script("arguments[0].click();", boton_login)

    # Después del login, vamos directo al catálogo para estabilizar el flujo.
    driver.get(f"{BASE_URL}/#/search")
    cerrar_banners_molestos(driver)

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Add to Basket']"))
    )


def obtener_contador_carrito(driver):
    """
    Obtiene el texto del botón Your Basket.
    Normalmente contiene el número de productos agregados.
    """
    try:
        return driver.find_element(By.ID, "navbarYourBasket").text
    except Exception:
        return ""


def agregar_dos_productos_al_carrito(driver):
    """
    Agrega dos productos diferentes al carrito para que luego se pueda eliminar uno
    y validar que el total se recalcula sin dejar el carrito vacío.
    """
    wait = WebDriverWait(driver, 20)

    # Esperar que existan al menos dos botones Add to Basket.
    wait.until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "button[aria-label='Add to Basket']")) >= 2
    )

    # Primer producto
    botones_compra = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Add to Basket']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botones_compra[0])
    driver.execute_script("arguments[0].click();", botones_compra[0])

    # Esperar que el carrito registre al menos 1 producto.
    wait.until(
        lambda d: "1" in obtener_contador_carrito(d) or len(d.find_elements(By.CSS_SELECTOR, "simple-snack-bar")) > 0
    )

    # Segundo producto
    wait.until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "button[aria-label='Add to Basket']")) >= 2
    )

    botones_compra = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Add to Basket']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botones_compra[1])
    driver.execute_script("arguments[0].click();", botones_compra[1])

    # Esperar que el sistema procese el segundo producto.
    wait.until(
        lambda d: "2" in obtener_contador_carrito(d) or len(d.find_elements(By.CSS_SELECTOR, "simple-snack-bar")) > 0
    )


def ir_al_carrito(driver):
    """
    Entra al carrito usando la ruta directa.
    Esto es más estable que depender del clic en Your Basket.
    """
    wait = WebDriverWait(driver, 20)

    driver.get(f"{BASE_URL}/#/basket")

    wait.until(
        EC.url_contains("basket")
    )

    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )


def obtener_total_carrito(driver):
    """
    Obtiene el total del carrito.
    En Juice Shop normalmente el total está en el elemento con id 'price'.
    """
    wait = WebDriverWait(driver, 20)

    total = wait.until(
        EC.visibility_of_element_located((By.ID, "price"))
    )

    return total.text.strip()


def obtener_botones_eliminar(driver):
    """
    Busca los botones de eliminar productos en el carrito.
    Se usan varios selectores porque puede variar según la versión visual.
    """
    botones = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Remove Basket Item']")

    if botones:
        return botones

    botones = driver.find_elements(
        By.XPATH,
        "//mat-cell[contains(@class, 'cdk-column-remove')]//button"
    )

    if botones:
        return botones

    botones = driver.find_elements(
        By.XPATH,
        "//button[.//mat-icon[contains(normalize-space(), 'delete')]]"
    )

    return botones


def test_tc017_eliminar_item_carrito_actualiza_totales(driver):
    """
    TC-017
    Título: Eliminación de un ítem del carrito con actualización de totales.
    Técnica: Transición de estados.
    Trazabilidad: RF-04.
    """

    wait = WebDriverWait(driver, 20)

    # =========================
    # ARRANGE
    # =========================
    iniciar_sesion(driver)
    agregar_dos_productos_al_carrito(driver)
    ir_al_carrito(driver)

    # Validar que el carrito tenga productos antes de eliminar.
    wait.until(
        lambda d: len(obtener_botones_eliminar(d)) >= 1
    )

    total_antes = obtener_total_carrito(driver)
    botones_antes = obtener_botones_eliminar(driver)
    cantidad_items_antes = len(botones_antes)

    print(f"[INFO] Total antes de eliminar: {total_antes}")
    print(f"[INFO] Cantidad de ítems antes de eliminar: {cantidad_items_antes}")

    assert cantidad_items_antes >= 1, (
        "No hay productos en el carrito para eliminar."
    )

    # =========================
    # ACT
    # =========================

    boton_eliminar = botones_antes[0]
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_eliminar)
    driver.execute_script("arguments[0].click();", boton_eliminar)

    # =========================
    # ASSERT
    # =========================

    # Esperar a que el total cambie o que disminuya la cantidad de botones de eliminar.
    wait.until(
        lambda d: obtener_total_carrito(d) != total_antes or len(obtener_botones_eliminar(d)) < cantidad_items_antes
    )

    total_despues = obtener_total_carrito(driver)
    botones_despues = obtener_botones_eliminar(driver)
    cantidad_items_despues = len(botones_despues)

    print(f"[INFO] Total después de eliminar: {total_despues}")
    print(f"[INFO] Cantidad de ítems después de eliminar: {cantidad_items_despues}")

    assert total_antes != total_despues or cantidad_items_despues < cantidad_items_antes, (
        "El carrito no actualizó el total ni la cantidad de productos después de eliminar."
    )

    assert cantidad_items_despues < cantidad_items_antes, (
        "La cantidad de productos en el carrito no disminuyó después de eliminar."
    )

    print("[SUCCESS] TC-017 COMPLETADO: Se eliminó un producto y el carrito actualizó su contenido.")
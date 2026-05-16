"""
TC-019: Búsqueda de producto existente en el catálogo - OWASP Juice Shop
Técnica: Particiones de equivalencia — partición válida
Trazabilidad: RF-03
Patrón AAA: Arrange - Act - Assert
"""

import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "http://localhost:3000"
SEARCH_TERM = "Apple"


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
    Intenta hacer clic sobre un elemento si existe.
    Sirve para cerrar banners o mensajes emergentes que pueden tapar la pantalla.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )
        driver.execute_script("arguments[0].click();", element)
    except Exception:
        pass


def cerrar_banners(driver):
    """
    Cierra banners comunes de OWASP Juice Shop.
    No falla si alguno no aparece.
    """
    safe_click(driver, By.CSS_SELECTOR, "button[aria-label='Close Welcome Banner']")
    safe_click(driver, By.CSS_SELECTOR, "a[aria-label='dismiss cookie message']")
    safe_click(driver, By.CSS_SELECTOR, "button[aria-label='dismiss cookie message']")
    safe_click(driver, By.XPATH, "//button[contains(., 'Me want it!')]")


def abrir_catalogo(driver):
    """
    Abre el catálogo principal de Juice Shop y espera a que carguen productos.
    """
    wait = WebDriverWait(driver, 20)

    driver.get(f"{BASE_URL}/#/search")
    cerrar_banners(driver)

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "mat-card"))
    )


def abrir_buscador(driver):
    """
    Abre el campo de búsqueda.
    Usa varios selectores para hacerlo más estable entre versiones de Juice Shop.
    """
    wait = WebDriverWait(driver, 20)

    posibles_selectores = [
        (By.CSS_SELECTOR, ".mat-search_icon-search"),
        (By.CSS_SELECTOR, "mat-icon.mat-search_icon-search"),
        (By.CSS_SELECTOR, "button[aria-label='Click to search']"),
        (By.XPATH, "//mat-icon[contains(normalize-space(), 'search')]"),
        (By.XPATH, "//button[.//mat-icon[contains(normalize-space(), 'search')]]"),
    ]

    for by, locator in posibles_selectores:
        try:
            elemento = wait.until(
                EC.presence_of_element_located((by, locator))
            )
            driver.execute_script("arguments[0].click();", elemento)
            return
        except Exception:
            continue

    raise AssertionError("No se pudo abrir el buscador del catálogo.")


def buscar_producto(driver, termino):
    """
    Escribe el término de búsqueda y ejecuta la búsqueda.
    """
    wait = WebDriverWait(driver, 20)

    posibles_inputs = [
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.CSS_SELECTOR, "input[aria-label='Text field for search query']"),
        (By.CSS_SELECTOR, "input[placeholder*='Search']"),
        (By.XPATH, "//input[contains(@aria-label, 'search') or contains(@placeholder, 'Search')]"),
    ]

    campo_busqueda = None

    for by, locator in posibles_inputs:
        try:
            campo_busqueda = wait.until(
                EC.element_to_be_clickable((by, locator))
            )
            break
        except Exception:
            continue

    if campo_busqueda is None:
        raise AssertionError("No se encontró el campo de texto para realizar la búsqueda.")

    campo_busqueda.clear()
    campo_busqueda.send_keys(termino)
    campo_busqueda.send_keys(Keys.ENTER)

    # Esperar a que la página procese el filtro.
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "mat-card"))
    )


def obtener_textos_productos_visibles(driver):
    """
    Obtiene los textos de las tarjetas de productos visibles en el catálogo.
    """
    wait = WebDriverWait(driver, 20)

    tarjetas = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "mat-card"))
    )

    textos = []

    for tarjeta in tarjetas:
        texto = tarjeta.text.strip()
        if texto:
            textos.append(texto)

    return textos


def guardar_evidencia(driver, nombre_archivo):
    """
    Guarda una captura de pantalla en la carpeta evidencias.
    """
    os.makedirs("evidencias", exist_ok=True)
    driver.save_screenshot(os.path.join("evidencias", nombre_archivo))


def test_tc019_busqueda_producto_existente_en_catalogo(driver):
    """
    TC-019
    Título: Búsqueda de producto existente en el catálogo.
    Técnica: Particiones de equivalencia — partición válida.
    Trazabilidad: RF-03.
    """

    # =========================
    # ARRANGE
    # =========================
    abrir_catalogo(driver)

    # =========================
    # ACT
    # =========================
    abrir_buscador(driver)
    buscar_producto(driver, SEARCH_TERM)

    guardar_evidencia(driver, "TC019_resultados_busqueda_apple.png")

    # =========================
    # ASSERT
    # =========================
    productos_visibles = obtener_textos_productos_visibles(driver)

    assert len(productos_visibles) > 0, (
        "No se mostraron productos después de ejecutar la búsqueda."
    )

    productos_con_apple = [
        producto for producto in productos_visibles
        if SEARCH_TERM.lower() in producto.lower()
    ]

    assert len(productos_con_apple) > 0, (
        f"No se encontraron productos relacionados con el término '{SEARCH_TERM}'. "
        f"Productos visibles: {productos_visibles}"
    )

    assert any("Apple Juice" in producto for producto in productos_visibles), (
        "No se encontró el producto esperado 'Apple Juice' dentro de los resultados."
    )

    print("[SUCCESS] TC-019 COMPLETADO: La búsqueda mostró productos relacionados con Apple.")
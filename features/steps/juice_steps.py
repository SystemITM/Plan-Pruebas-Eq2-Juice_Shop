from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


def click_if_visible(driver, locator, timeout=3):
    """
    Intenta hacer clic en un elemento si aparece.
    Sirve para cerrar banners o mensajes iniciales sin romper la prueba.
    """
    try:
        quick_wait = WebDriverWait(driver, timeout)
        element = quick_wait.until(EC.element_to_be_clickable(locator))
        element.click()
    except TimeoutException:
        pass


def close_initial_popups(context):
    """
    Cierra ventanas iniciales comunes de Juice Shop:
    - Welcome banner
    - Cookie banner
    """

    driver = context.driver

    possible_buttons = [
        (By.CSS_SELECTOR, "button[aria-label='Close Welcome Banner']"),
        (By.XPATH, "//button[contains(., 'Dismiss')]"),
        (By.CSS_SELECTOR, "a[aria-label='dismiss cookie message']"),
        (By.XPATH, "//span[contains(., 'Dismiss')]"),
    ]

    for locator in possible_buttons:
        click_if_visible(driver, locator, timeout=3)


@given("a working BDD setup")
def step_working_bdd_setup(context):
    context.bdd_ready = True


@when("the engine processes this scenario")
def step_engine_processes_scenario(context):
    context.engine_processed = context.bdd_ready


@then("the scenario passes successfully")
def step_scenario_passes_successfully(context):
    assert context.engine_processed is True


@given("OWASP Juice Shop is running locally")
def step_juice_shop_running_locally(context):
    context.driver.get(context.base_url)

    context.wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    close_initial_popups(context)

    page_text = context.driver.page_source.lower()
    assert "juice shop" in page_text or "owasp" in page_text


@when("the user searches for an existing product keyword")
def step_user_searches_existing_product(context):
    driver = context.driver
    wait = context.wait

    search_icon = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".mat-search_icon-search"))
    )
    search_icon.click()

    search_input = wait.until(
        EC.visibility_of_element_located((By.ID, "searchQuery"))
    )
    search_input.clear()
    search_input.send_keys("Apple")
    search_input.send_keys(Keys.ENTER)


@then("the product catalog displays matching Apple products")
def step_catalog_displays_matching_products(context):
    wait = context.wait

    wait.until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Apple")
    )

    page_text = context.driver.page_source.lower()

    assert "apple" in page_text, "No se encontraron productos relacionados con Apple."
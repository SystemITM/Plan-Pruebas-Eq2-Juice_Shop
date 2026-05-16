@"
# Suite mínima ejecutable - Equipo 2 - OWASP Juice Shop

## SUT
OWASP Juice Shop ejecutándose localmente en:

http://localhost:3000

## Herramientas utilizadas
- Python
- Selenium WebDriver
- Pytest
- WebDriver Manager
- Pytest HTML

## Casos automatizados
- TC-003: Inicio de sesión con credenciales válidas.
- TC-004: Inicio de sesión con contraseña incorrecta.
- TC-016: Transición exitosa de producto del catálogo al carrito.
- TC-017: Eliminación de ítem del carrito con actualización de totales.

## Instalación de dependencias
Ejecutar:

pip install -r requirements.txt

## Ejecución de la suite
Desde la carpeta principal del proyecto, ejecutar:

pytest .\tests -v --html=Reporte-HTML-Eq2-Juice_Shop.html --self-contained-html

## Nota
Antes de ejecutar las pruebas, OWASP Juice Shop debe estar iniciado localmente en el puerto 3000.
"@ | Set-Content ".\Codigo-Eq2-Juice_Shop\README.md" -Encoding UTF8
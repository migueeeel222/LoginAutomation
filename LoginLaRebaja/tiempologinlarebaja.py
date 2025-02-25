"""
Módulo para manejar los tiempos de login y cierre de sesión.
Optimiza la medición de tiempos de carga y cierre de sesión en Selenium.
"""

import logging
import time
from datetime import datetime
from loginlarebaja import (
    obtener_ip, iniciar_driver, abrir_pagina, clic_mi_cuenta,
    ingresar_credenciales, clic_ingresar, confirmar_login, salir_cuenta,
    autenticado_salir, guardar_en_google_sheets, cerrar_navegador
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def ejecutar_prueba():
    """
    Ejecuta el flujo de login, mide los tiempos y los almacena en Google Sheets.
    """
    driver = iniciar_driver()
    if not driver:
        return

    dia = datetime.now().strftime("%Y/%m/%d")
    hora_de_inicio = datetime.now().strftime("%H:%M:%S")
    usuario = "pruebaslogin360@gmail.com"
    ip = obtener_ip()

    # Medir tiempo de carga real del formulario de login
    tiempo_inicio = time.time()
    abrir_pagina(driver)
    tiempo_renderizado_formulario_login = round(time.time() - tiempo_inicio, 3)  # Tiempo real

    # Medir tiempo hasta que se carga la página de inicio después del login
    tiempo_inicio = time.time()
    clic_mi_cuenta(driver)
    tiempo_renderizado_home = round(time.time() - tiempo_inicio, 3)

    # Ingresar credenciales y medir tiempo de autenticación
    ingresar_credenciales(driver)
    clic_ingresar(driver)

    tiempo_inicio = time.time()
    confirmar_login(driver)

    # Cerrar sesión desde "Mi Cuenta"
    tiempo_inicio = time.time()
    tiempo_cerrar_mi_cuenta = salir_cuenta(driver) or 0
    tiempo_cerrar_mi_cuenta = round(time.time() - tiempo_inicio, 3)

    # Cerrar sesión completa y medir tiempo total
    tiempo_inicio = time.time()
    tiempo_autenticado_salir = autenticado_salir(driver) or 0
    tiempo_autenticado_salir = round(time.time() - tiempo_inicio, 3)

    # Estado basado en tiempos válidos
    estado = "Exitoso" if all([tiempo_renderizado_formulario_login, tiempo_renderizado_home, tiempo_cerrar_mi_cuenta, tiempo_autenticado_salir]) else "Fallido"

    # Guardar en Google Sheets evitando valores None
    datos = [dia, hora_de_inicio, usuario, ip,
             tiempo_renderizado_formulario_login,
             tiempo_renderizado_home,
             tiempo_cerrar_mi_cuenta,
             tiempo_autenticado_salir,
             estado]

    guardar_en_google_sheets(datos)
    cerrar_navegador(driver)

    logging.info("Prueba completada: %s", datos)
if __name__ == "__main__":
    ejecutar_prueba()

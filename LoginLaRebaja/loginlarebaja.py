"""
Script para automatizar el login en la tienda virtual. Captura los tiempos de carga, 
realiza el proceso de inicio y cierre de sesión y guarda los datos en Google Sheets.
"""

import logging
import time
import socket
from datetime import datetime
from typing import Callable, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuración de Selenium y Google Sheets
CHROMEDRIVER_PATH = r"C:\\Users\\mreyes\\Documents\\LoginLaRebaja\\chromedriver-win64\\chromedriver.exe"
CREDENTIALS_PATH = r"C:\\Users\\mreyes\\Documents\\LoginLaRebaja\\silicon-park-451318-q3-2e720cc1e169.json"
SPREADSHEET_ID = "1EcCiF1nRMfqKgHv7z4wPxy-QRvW1z2-sLQXlZSvgDgw"
SHEET_NAME = "TiemposAutomatización"

# Obtener la IP del equipo
def obtener_ip() -> str:
    """
    Obtiene la dirección IP del equipo.
    """
    try:
        return socket.gethostbyname(socket.gethostname())
    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        logging.error("Error obteniendo la IP: %s", e)
        return "Desconocida"

def iniciar_driver() -> Optional[webdriver.Chrome]:
    """
    Inicia el driver de Selenium con las opciones configuradas.
    """
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-background-timer-throttling")  # <- Agregado
        options.add_argument("--disable-backgrounding-occluded-windows")  # <- Agregado
        options.add_argument("--disable-renderer-backgrounding")  # <- Agregado
        service = Service(CHROMEDRIVER_PATH)
        return webdriver.Chrome(service=service, options=options)
    except WebDriverException as e:
        logging.error("Error al iniciar el driver: %s", e)
        return None


# Decorador para medir tiempos
def medir_tiempo(func: Callable[..., Optional[float]]) -> Callable[..., Optional[float]]:
    """
    Decorador que mide el tiempo de ejecución de una función y lo registra en logs.
    """
    def wrapper(*args, **kwargs) -> Optional[float]:
        inicio = time.time()
        try:
            resultado = func(*args, **kwargs)
            fin = time.time()
            duracion = round(fin - inicio, 3)
            logging.info("Tiempo de %s: %.3f segundos", func.__name__, duracion)
            print(f"Tiempo de {func.__name__}: {duracion} segundos")
            return duracion if resultado is None else resultado
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logging.error("Error en %s: %s", func.__name__, e)
            return None
    return wrapper

@medir_tiempo
def abrir_pagina(driver: webdriver.Chrome):
    """
    Abre la página principal de la tienda virtual.
    """
    driver.get("https://www.larebajavirtual.com/")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

@medir_tiempo
def clic_mi_cuenta(driver: webdriver.Chrome) -> Optional[float]:
    """
    Hace clic en el botón "Mi Cuenta" para acceder al formulario de login.
    """
    boton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div[6]/div/div/button/div/span/div/div/span"))
    )
    inicio = time.time()
    boton.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='email']")))
    fin = time.time()
    tiempo_renderizado_formulario = round(fin - inicio, 3)
    logging.info("Tiempo de Renderizado del Formulario de Login: %.3f segundos", tiempo_renderizado_formulario)
    print(f"Tiempo de Renderizado del Formulario de Login: {tiempo_renderizado_formulario} segundos")
    return tiempo_renderizado_formulario

@medir_tiempo
def ingresar_credenciales(driver: webdriver.Chrome):
    """
    Ingresa el usuario y contraseña en el formulario de login.
    """
    user_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='email']")))
    pass_input = driver.find_element(By.XPATH, "//input[@formcontrolname='password']")
    user_input.send_keys("pruebaslogin360@gmail.com")
    pass_input.send_keys("Clave12345678*")

@medir_tiempo
def clic_ingresar(driver: webdriver.Chrome) -> Optional[float]:
    """
    Hace clic en el botón "Ingresar" para iniciar sesión.
    """
    boton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/app-login/div/div/div/div/form/button/span"))
    )
    inicio = time.time()
    boton.click()

    # Esperar hasta que la URL cambie (indicando que el login fue exitoso)
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

    # Esperar hasta que un elemento clave del home esté visible
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'header')]"))  # Ajusta esto según el home
        )
    except TimeoutException:
        logging.error("Error: No se detectó el home después de iniciar sesión.")
        driver.quit()
        return None

    fin = time.time()
    tiempo_renderizado_home = round(fin - inicio, 3)
    logging.info("Tiempo de Renderizado del Home de la Tienda Virtual: %.3f segundos", tiempo_renderizado_home)
    print(f"Tiempo de Renderizado del Home de la Tienda Virtual: {tiempo_renderizado_home} segundos")

    return tiempo_renderizado_home


@medir_tiempo
def confirmar_login(driver: webdriver.Chrome):
    """
    Confirma el inicio de sesión si es necesario.
    """
    boton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Confirmar']")))
    boton.click()

@medir_tiempo
def salir_cuenta(driver: webdriver.Chrome):
    """
    Cierra sesión desde la sección "Mi Cuenta".
    """
    try:
        boton_cuenta = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "(//div[@class='vtex-button__label flex items-center justify-center h-100 ph6 '])[1]"))
        )
        boton_cuenta.click()
        boton_salir = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Salir']"))
        )
        boton_salir.click()
    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        logging.error("ERROR en salir_cuenta: %s", e)

@medir_tiempo
def autenticado_salir(driver: webdriver.Chrome):
    """
    Cierra sesión desde la autenticación del usuario.
    """
    try:
        boton_salir = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Salir']")))
        boton_salir.click()
    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        logging.error("Error en autenticado_Salir: %s", e)

def cerrar_navegador(driver: webdriver.Chrome):
    """
    Cierra el navegador de manera segura.
    """
    driver.quit()


def guardar_en_google_sheets(datos: list):
    """
    Guarda los datos de los tiempos de ejecución en una hoja de cálculo de Google Sheets.
    Inserta los nuevos datos en la primera fila de datos y desplaza los registros anteriores hacia abajo.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        sheet.insert_row(datos, index=2)  # Inserta en la segunda fila, manteniendo los encabezados
        logging.info("Datos insertados en Google Sheets correctamente.")
    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        logging.error("Error al guardar en Google Sheets: %s", e)


if __name__ == "__main__":
    while True:  # Bucle infinito para ejecutar cada 5 minutos
        DRIVER = iniciar_driver()
        if not DRIVER:
            exit()

        DIA = datetime.now().strftime("%Y/%m/%d")
        HORA_DE_INICIO = datetime.now().strftime("%H:%M:%S")
        USUARIO = "pruebaslogin360@gmail.com"
        IP = obtener_ip()

        abrir_pagina(DRIVER)

        # Medición correcta del tiempo de renderizado del formulario de login
        inicio_tiempo_formulario = time.time()
        TIEMPO_RENDERIZADO_FORMULARIO_LOGIN = clic_mi_cuenta(DRIVER)
        if TIEMPO_RENDERIZADO_FORMULARIO_LOGIN is None:
            TIEMPO_RENDERIZADO_FORMULARIO_LOGIN = round(time.time() - inicio_tiempo_formulario, 3)

        ingresar_credenciales(DRIVER)
        clic_ingresar(DRIVER)
        confirmar_login(DRIVER)

        # Medición correcta del tiempo hasta que se renderiza el home
        inicio_tiempo_home = time.time()
        WebDriverWait(DRIVER, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Espera el home
        TIEMPO_RENDERIZADO_HOME = round(time.time() - inicio_tiempo_home, 3)

        time.sleep(5)

        TIEMPO_CERRAR_MI_CUENTA = salir_cuenta(DRIVER)
        if TIEMPO_CERRAR_MI_CUENTA is None:
            TIEMPO_CERRAR_MI_CUENTA = 0  # Si no se registra tiempo, asigna 0

        # Se asegura de que `autenticado_Salir` retorne un valor
        inicio_tiempo_autenticado = time.time()
        TIEMPO_AUTENTICADO_SALIR = autenticado_salir(DRIVER)
        if TIEMPO_AUTENTICADO_SALIR is None:
            TIEMPO_AUTENTICADO_SALIR = round(time.time() - inicio_tiempo_autenticado, 3)

        # Se determina el estado correctamente
        ESTADO = "Exitoso" if all([TIEMPO_RENDERIZADO_FORMULARIO_LOGIN, TIEMPO_RENDERIZADO_HOME,
                                   TIEMPO_CERRAR_MI_CUENTA, TIEMPO_AUTENTICADO_SALIR]) else "Fallido"

        # Se corrige el orden de la lista `DATOS`
        DATOS = [DIA, HORA_DE_INICIO, USUARIO, IP, TIEMPO_RENDERIZADO_FORMULARIO_LOGIN,
                 TIEMPO_RENDERIZADO_HOME, TIEMPO_CERRAR_MI_CUENTA, TIEMPO_AUTENTICADO_SALIR, ESTADO]

        guardar_en_google_sheets(DATOS)
        cerrar_navegador(DRIVER)

        logging.info("Esperando 5 minutos antes de la próxima ejecución...")
        time.sleep(300)  # Espera 300 segundos (5 minutos)

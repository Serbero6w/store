import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configuración del navegador
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://web.whatsapp.com/")
print("Escanea el código QR en WhatsApp Web para continuar.")
time.sleep(15)  # Esperar a que el usuario escanee el QR

# Cargar productos desde carpetas
PRODUCTOS_DIR = "productos"
PRODUCTOS = {}

for producto_id, carpeta in enumerate(os.listdir(PRODUCTOS_DIR), start=1):
    carpeta_path = os.path.join(PRODUCTOS_DIR, carpeta)
    if os.path.isdir(carpeta_path):
        PRODUCTOS[str(producto_id)] = {
            "nombre": carpeta,
            "foto": os.path.join(carpeta_path, "foto.jpg"),
            "video": os.path.join(carpeta_path, "video.mp4"),
            "descripcion": os.path.join(carpeta_path, "descripcion.txt"),
            "precio": os.path.join(carpeta_path, "precio.txt"),
        }

# Validaciones
def validar_contacto(contacto):
    return contacto.isdigit() and len(contacto) == 8

def validar_nombre(nombre):
    return nombre.replace(" ", "").isalpha() and len(nombre) > 2

# Bot principal
def escuchar_mensajes():
    while True:
        try:
            mensajes = driver.find_elements(By.XPATH, '//span[@class="_11JPr selectable-text copyable-text"]')
            if not mensajes:
                time.sleep(3)
                continue
            
            ultimo_mensaje = mensajes[-1].text.lower()
            print(f"Mensaje recibido: {ultimo_mensaje}")

            if "hola" in ultimo_mensaje:
                enviar_mensaje("¡Hola! Bienvenido a nuestra tienda. Escribe 'menu' para ver nuestros productos.")
            elif "menu" in ultimo_mensaje:
                mostrar_menu()
            elif ultimo_mensaje in PRODUCTOS.keys():
                enviar_producto(ultimo_mensaje)
            elif "confirmar" in ultimo_mensaje:
                recolectar_datos()
            else:
                enviar_mensaje("Lo siento, no entiendo tu mensaje. Escribe 'menu' para comenzar.")
            
            time.sleep(3)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

def enviar_mensaje(mensaje):
    try:
        message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true" and @data-tab="1"]')
        message_box.send_keys(mensaje)
        message_box.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

def mostrar_menu():
    menu = "Menú de productos:\n"
    for key, producto in PRODUCTOS.items():
        menu += f"{key}. {producto['nombre']}\n"
    menu += "Por favor, responde con el número del producto para más información."
    enviar_mensaje(menu)

def enviar_producto(producto_id):
    producto = PRODUCTOS[producto_id]
    enviar_mensaje(f"Has seleccionado: {producto['nombre']}.")
    
    if os.path.exists(producto["descripcion"]):
        with open(producto["descripcion"], "r") as desc_file:
            descripcion = desc_file.read()
        enviar_mensaje(descripcion)
    
    if os.path.exists(producto["precio"]):
        with open(producto["precio"], "r") as precio_file:
            precio = precio_file.read()
        enviar_mensaje(f"Precio: ${precio} USD.")
    
    adjuntar_archivo(producto["foto"])
    if os.path.exists(producto["video"]):
        adjuntar_archivo(producto["video"])
    
    enviar_mensaje("Si deseas confirmar este producto, escribe 'confirmar'.")

def adjuntar_archivo(ruta_archivo):
    try:
        clip = driver.find_element(By.XPATH, '//span[@data-icon="clip"]')
        clip.click()
        time.sleep(1)
        attach = driver.find_element(By.XPATH, '//input[@accept="*"]')
        attach.send_keys(os.path.abspath(ruta_archivo))
        time.sleep(2)
        enviar_btn = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
        enviar_btn.click()
    except Exception as e:
        print(f"Error al adjuntar archivo: {e}")

def recolectar_datos():
    enviar_mensaje("Por favor, escribe tu nombre completo:")
    time.sleep(10)
    nombre = obtener_ultimo_mensaje()

    if not validar_nombre(nombre):
        enviar_mensaje("El nombre ingresado no es válido. Por favor, escribe tu nombre completo correctamente.")
        return

    enviar_mensaje("Ahora, envía tu número de contacto:")
    time.sleep(10)
    contacto = obtener_ultimo_mensaje()

    if not validar_contacto(contacto):
        enviar_mensaje("El número de contacto no es válido. Debe contener 8 dígitos.")
        return

    enviar_mensaje("Finalmente, comparte tu ubicación:")
    time.sleep(20)
    enviar_mensaje("¡Gracias! Tu pedido está siendo procesado.")
    reenviar_a_delivery(nombre, contacto)

def obtener_ultimo_mensaje():
    mensajes = driver.find_elements(By.XPATH, '//span[@class="_11JPr selectable-text copyable-text"]')
    return mensajes[-1].text if mensajes else ""

def reenviar_a_delivery(nombre, contacto):
    enviar_mensaje("Resumen del pedido:")
    enviar_mensaje(f"Cliente: {nombre}\nContacto: {contacto}\nProducto: Confirmado\nUbicación: Compartida.")

# Ejecutar el bot
if __name__ == "__main__":
    try:
        escuchar_mensajes()
    except KeyboardInterrupt:
        print("Bot detenido.")
    finally:
        driver.quit()

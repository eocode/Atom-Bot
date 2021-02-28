# Load Telebot
import telebot
from platform import system
import os
import hashlib

# Load environment variables
import os
from dotenv import load_dotenv

load_dotenv()

from gtts import gTTS
from playsound import playsound

thisOS = system()

# Load tts
import pyttsx3

# Init Arthur
bot = telebot.TeleBot(os.environ["telegram_token_bot"])
knownUsers = os.environ["telegram_users"].split(",")

# list of available commands
commands = {
    "start": "Primeros pasos",
    "help": "Comandos soportados",
    "stats": "Estadísticas actuales del BTCMXN",
    "mxn_btc": "Convierte pesos mexicanos a BTC",
    "btc_mxn": "Convierte BTC a pesos mexicanos",
    "operation": "Realiza los cálculos para una operación en este momento",
    "simulation": "Simula una operación con un monto de inversión y un precio futuro del mercado",
    "monitor": "Monitorea el precio del BTC por 5 min si tienes una operación abierta",
    "monitor_trade": "Alerta de valor minimo",
    "smart_alerts": "Ejecuta un monitor inteligente que te enviará notificaciones de forma automática (BETA)",
}

# Bot listener
def listener(messages):
    for m in messages:
        if m.content_type == "text":
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


# Init bot listener
def init(instance):
    instance.set_update_listener(listener)


def send_voice(text):
    file = hashlib.md5(text.encode()).hexdigest() + ".mp3"
    if thisOS == "Linux":
        tts = gTTS(text, lang="es", tld="com.mx")
        tts.save(file)
        os.system("mpg123 " + file)
    if thisOS == "Windows":
        tts = gTTS(text, lang="es", tld="com.mx")
        tts.save(file)
        playsound(file)
    os.remove(file)


def say_hello():
    send_voice("Hola mi nombre es: " + os.environ["bot_name"])
    send_voice("Versión: " + os.environ["bot_version"])
    send_voice("A partir de ahora estoy activa en conjunto con Alexa")

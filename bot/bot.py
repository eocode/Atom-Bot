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

# Init Arthur
bot = telebot.TeleBot(os.environ["telegram_token_bot"])
knownUsers = os.environ["telegram_users"].split(",")
name = os.environ["bot_name"]
version = "0.1.5"

# list of available commands
commands = {
    "start": "Primeros pasos y bienvenida",
    "get_cid": "Obten tu identificador único de usuario, este es agregado a la lista blanca para tener una experiencia personalizada, así como desbloquear funcionalidades adicionales en el bot, daselo al administrador del BOT para tener acceso",
    "info": "Información acerca del bot",
    "help": "Lista de los comandos soportados",
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
    send_voice("Iniciando ... " + name + " " + version)

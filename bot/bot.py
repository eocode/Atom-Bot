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
version = "0.1.6"

# list of available commands
# Common commands
commands = {
    "start": "Primeros pasos y bienvenida",
    "info": "Información acerca del bot",
    "help": "Lista de los comandos soportados"
}

# Personal commands
commands["get_cid"] = "Obten tu identificador único de usuario, deberás proporcionarlo al administrador"

# Crypto commands
commands["crypto_set_market"] = "Asigna el mercado actual con el cuál trabajar"
commands["crypto_get_stats"] = "Estadísticas actuales del mercado seleccionado"
commands["mxn_btc"] = "Convierte pesos mexicanos a BTC"
commands["btc_mxn"] = "Convierte BTC a pesos mexicanos"
commands["operation"] = "Realiza los cálculos para una operación en este momento"
commands["simulation"] = "Simula una operación con un monto de inversión y un precio futuro del mercado"
commands["monitor"] = "Monitorea el precio del BTC por 5 min si tienes una operación abierta"
commands["monitor_trade"] = "Alerta de valor minimo"
commands["smart_alerts"] = "Ejecuta un monitor inteligente que te enviará notificaciones de forma automática (BETA)"

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

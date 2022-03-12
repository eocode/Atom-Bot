# Load Telebot
import telebot
import os

# Load environment variables
from dotenv import load_dotenv

# from modules.financing.data.trader import initialize_operatives

load_dotenv()

# Init
bot = telebot.TeleBot(os.environ["telegram_token_bot"])
telebot.apihelper.SESSION_TIME_TO_LIVE = 5 * 60

# list of available commands
# Common commands
commands = {"start": "Primeros pasos y bienvenida",
            "acerca": "Conoce a " + os.environ["bot_name"],
            "ayuda": "Lista de los comandos",
            "configuracion": "Tus ajustes actuales",
            "elegir_mercado": "Selecciona un mercado",
            "ver_graficos": "Indicadores de trade",
            "trade": "Recibe recomendaciones",
            "simular_trades": "Realiza un backtest",
            "alertas": "Ver operativas"}


# Personal commands

# # Crypto commands


# Bot listener
def listener(messages):
    for m in messages:
        if m.content_type == "text":
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


# Init bot listener
def init(instance):
    instance.set_update_listener(listener)

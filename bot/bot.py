# Load Telebot
import telebot
import os

# Load environment variables
from dotenv import load_dotenv

# from modules.financing.data.trader import initialize_operatives

load_dotenv()

# Init
bot = telebot.TeleBot(os.environ["telegram_token_bot"])

# list of available commands
# Common commands
commands = {
    "start": "Primeros pasos y bienvenida",
    "acerca": "Información acerca de " + os.environ["bot_name"],
    "ayuda": "Lista de los comandos"
}

# Personal commands
commands["mi_id"] = "Obten tu identificador único"
commands["configuracion"] = "Tus ajustes actuales"

# # Crypto commands
commands["elegir_mercado"] = "Selecciona un mercado"
commands["ver_graficos"] = "Indicadores de trade"
commands["trade"] = "Recibe recomendaciones"
commands["ver_analisis"] = "Ver analisis general"
commands["ver_resumen"] = "Resumen del analisis"
commands["simular_trades"] = "Realiza un backtest"
commands["trade_actual"] = "Revisa la última operativa"


# Bot listener
def listener(messages):
    for m in messages:
        if m.content_type == "text":
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


# Init bot listener
def init(instance):
    instance.set_update_listener(listener)

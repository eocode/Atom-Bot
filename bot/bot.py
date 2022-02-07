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
commands["elegir_mercado"] = "Para tus operaciones"
# commands["crypto_get_stats"] = "Estadísticas actuales del mercado seleccionado"
# commands["crypto_convert_second_to_first"] = "Convierte de acuerdo a tus configuraciones"
# commands["crypto_convert_first_to_second"] = "Convierte de acuerdo a tus configuraciones"
# commands["operation"] = "Realiza los cálculos para una operación en este momento"
# commands["simulation"] = "Simula una operación con un monto de inversión y un precio futuro del mercado"
# commands["monitor"] = "Monitorea el precio del BTC por 5 min si tienes una operación abierta"
# commands["monitor_trade"] = "Alerta de valor minimo"
# commands["smart_alerts"] = "Ejecuta un monitor inteligente que te enviará notificaciones de forma automática (BETA)"
commands["ver_graficos"] = "Indicadores de trade"
commands["trade"] = "Recibe recomendaciones"
commands["ver_analisis"] = "Ver analisis general"
commands["ver_resumen"] = "Resumen del analisis"


# Bot listener
def listener(messages):
    for m in messages:
        if m.content_type == "text":
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


# Init bot listener
def init(instance):
    instance.set_update_listener(listener)
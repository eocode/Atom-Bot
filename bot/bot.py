# Load Telebot
import telebot
import os

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Init
bot = telebot.TeleBot(os.environ["telegram_token_bot"])

# list of available commands
# Common commands
commands = {
    "start": "Primeros pasos y bienvenida",
    "acerca_de_tu_bot": "Información acerca del bot",
    "ayuda": "Lista de los comandos"
}

# Personal commands
commands["mi_identificador"] = "Obten tu identificador único"
commands["mi_configuracion"] = "Obten las configuraciones que ada tiene sobre tí"

# # Crypto commands
commands["configurar_mercado"] = "Asigna el mercado actual para realizar las operaciones"
commands["crypto_get_stats"] = "Estadísticas actuales del mercado seleccionado"
commands["crypto_convert_second_to_first"] = "Convierte de acuerdo a tus configuraciones"
commands["crypto_convert_first_to_second"] = "Convierte de acuerdo a tus configuraciones"
commands["operation"] = "Realiza los cálculos para una operación en este momento"
commands["simulation"] = "Simula una operación con un monto de inversión y un precio futuro del mercado"
commands["monitor"] = "Monitorea el precio del BTC por 5 min si tienes una operación abierta"
commands["monitor_trade"] = "Alerta de valor minimo"
commands["smart_alerts"] = "Ejecuta un monitor inteligente que te enviará notificaciones de forma automática (BETA)"
commands["ver_graficos"] = "Obten los gráficos de una crypto para tomar decisiones"
commands["trade"] = "Realiza trades con recomendaciones del bot"
commands["preparar_operativa"] = "Prepara la operativa a realizar"


# Bot listener
def listener(messages):
    for m in messages:
        if m.content_type == "text":
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


# Init bot listener
def init(instance):
    instance.set_update_listener(listener)

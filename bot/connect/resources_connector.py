from bot.connect.message_connector import send_initial_message
from modules.core.model import get_groups
from modules.financing.crypto.data.operative import operatives, initialize_operatives, start_operatives
from bot.constants import version


def show_operatives(symbol):
    operatives[symbol].monitor.show_operative()


def get_monitor(symbol):
    return operatives[symbol].monitor


def init_operatives():
    initialize_operatives()
    groups = []
    for group in get_groups():
        groups.append(group.id)
        send_initial_message(chat_id=group.id,
                             text="Actualizando a la versión %s\nNOTA: Es posible que se pierda el seguimiento de algunos trades, tome precauciones" % version)
    start_operatives(groups)

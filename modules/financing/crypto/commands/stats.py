from bot.bot import bot
from modules.financing.crypto.operations import get_stats
from modules.core.model.account import get_settings
from connect.communication import send_message, valid_user


@bot.message_handler(commands=["crypto_get_stats"])
def command_start(m):
    cid = m.chat.id
    try:
        if valid_user(cid):
            bot.send_chat_action(cid, "typing")
            market = get_settings(cid).current_market
            message = get_stats(market)
            send_message(cid, message)
        else:
            send_message(cid, "Lo siento, no tienes permisos para realizar está acción")
    except Exception as e:
        print(e)
        print("Ocurrio un error al obtener los datos")
        send_message(cid, "Lo siento, ocurrio un error")
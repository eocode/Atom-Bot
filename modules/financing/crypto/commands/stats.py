from bot.bot import bot, knownUsers
from modules.financing.crypto.operations import get_stats
from modules.core.model.account import get_settings


@bot.message_handler(commands=["crypto_get_stats"])
def command_start(m):
    cid = m.chat.id
    try:
        if str(cid) in knownUsers:
            bot.send_chat_action(cid, "typing")
            market = get_settings(cid).current_market
            message = get_stats(market)
            bot.send_message(cid, message)
        else:
            bot.send_message(cid, "Lo siento, no tienes permisos para realizar está acción")
    except Exception as e:
        print(e)
        print("Ocurrio un error al obtener los datos")
        bot.send_message(cid, "Lo siento, ocurrio un error")
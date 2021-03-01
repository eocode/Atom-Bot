from bot.bot import bot, knownUsers
from trader_pro.btc import show_btc_stats
from data.models.settings import get_settings


@bot.message_handler(commands=["crypto_get_stats"])
def command_start(m):
    try:
        cid = m.chat.id
        if str(cid) in knownUsers:
            bot.send_chat_action(cid, "typing")
            market = get_settings(cid).current_market
            message = show_btc_stats(market)
            bot.send_message(cid, message)
        else:
            bot.send_message(cid, "Lo siento, no tienes permisos para realizar está acción")
    except Exception as e:
        print(e)
        print("Ocurrio un error al obtener los datos")
from bot.bot import bot
from trader_pro.btc import show_btc_stats
from data.models.settings import get_market


@bot.message_handler(commands=["crypto_get_stats"])
def command_start(m):
    try:
        cid = m.chat.id
        bot.send_chat_action(cid, "typing")
        market = get_market(cid).current_market
        print(market)
        message = show_btc_stats(market)
        bot.send_message(cid, message)
    except Exception as e:
        print(e)
        print("Ocurrio un error al obtener los datos")
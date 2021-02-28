from bot.bot import bot
from trader_pro.btc import show_btc_stats


@bot.message_handler(commands=["stats"])
def command_start(m):
    cid = m.chat.id
    bot.send_chat_action(cid, "typing")
    message = show_btc_stats()
    bot.send_message(cid, message)
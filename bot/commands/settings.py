from bot.bot import bot
from data.models.settings import update_market
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


@bot.message_handler(commands=["crypto_set_market"])
def set_current_market(message):
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("btc_mxn"), KeyboardButton("eth_mxn"))
    msg = bot.reply_to(
        message,
        "¿Cuál es el libro con el que quieres operar?",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, set_current_market_option)


def set_current_market_option(message):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        market = message.text
        update_market(cid, market)
        bot.send_message(cid, "Valor actualizado a " + market)
    except Exception as e:
        print(e)
        bot.reply_to(message, "Algo salio mal al obtener los valores")
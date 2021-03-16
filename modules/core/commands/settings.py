from bot.bot import bot
from modules.core.model.settings import get_settings, update_market
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


@bot.message_handler(commands=["crypto_set_market"])
def set_current_market(m):
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("btc_mxn"), KeyboardButton("eth_mxn"))
    msg = bot.reply_to(
        m,
        "¿Cuál es el libro con el que quieres operar?",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, set_current_market_option)


def set_current_market_option(m):
    try:
        cid = m.chat.id
        bot.send_chat_action(cid, "typing")
        market = m.text
        update_market(cid, market)
        bot.send_message(cid, "Valor actualizado a " + market)
    except Exception as e:
        print(e)
        bot.reply_to(m, "Algo salio mal al obtener los valores")


@bot.message_handler(commands=["get_my_settings"])
def get_my_settings(m):
    try:
        cid = m.chat.id
        bot.send_chat_action(cid, "typing")
        settings = get_settings(cid)
        bot.send_message(cid, settings)
    except Exception as e:
        print(e)
        bot.reply_to(m, "Algo salio mal al obtener tus datos")
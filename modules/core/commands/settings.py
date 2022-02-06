from bot.bot import bot
from modules.core.model.account import get_settings, update_market
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from modules.financing.crypto.dictionary import bitso_order_books, binance_order_books
from modules.core.data.user import User, user_data
from bot.connect.communication import send_message


@bot.message_handler(commands=["configurar_mercado"])
def set_exchange(m):
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("Bitso"), KeyboardButton("Binance"))
    msg = bot.reply_to(
        m,
        "¿Elige una opción?",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, set_market)


def set_market(m):
    cid = m.chat.id
    exchange = m.text
    user = User()
    user.platform = exchange
    user_data[cid] = user
    markup = ReplyKeyboardMarkup(row_width=2)
    if exchange == 'Bitso':
        for book in bitso_order_books:
            markup.add(KeyboardButton(book))
    else:
        if exchange == 'Binance':
            for book in binance_order_books:
                markup.add(KeyboardButton(book))
        else:
            send_message(cid, "Valor invalido")
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
        user = user_data[cid]
        if user.platform == 'Bitso':
            user.market = bitso_order_books[m.text]
        else:
            if user.platform == 'Binance':
                user.market = binance_order_books[m.text]
        update_market(cid, user.market, m.text, user.platform)
        send_message(cid, "Valor actualizado a " + m.text)
    except Exception as e:
        print(e)
        bot.reply_to(m, "Algo salio mal al obtener los valores")


@bot.message_handler(commands=["mi_configuracion"])
def my_settings(m):
    try:
        cid = m.chat.id
        bot.send_chat_action(cid, "typing")
        settings = get_settings(cid)
        send_message(cid, settings)
    except Exception as e:
        print(e)
        bot.reply_to(m, "Algo salio mal al obtener tus datos")

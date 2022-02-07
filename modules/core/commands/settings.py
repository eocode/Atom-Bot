from bot.bot import bot
from modules.core.model.account import get_settings, update_market
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from modules.financing.connector.binance.trader import CryptoBot
from modules.financing.crypto.dictionary import bitso_order_books, binance_order_books
from modules.core.data.user import User, user_data, get_user_info, save_user_info
from bot.connect.communication import send_message
from modules.financing.data.trader import operatives, TraderOPS


@bot.message_handler(commands=["elegir_mercado"])
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
                user.market = binance_order_books[m.text]['symbol']
                user.crypto = binance_order_books[m.text]['crypto']
                user.pair = binance_order_books[m.text]['pair']
        update_market(cid, user.crypto, user.pair, user.market, m.text, user.platform)
        send_message(cid, "Valor actualizado a " + m.text, close_markup=True)
        prepare(user, cid)
    except Exception as e:
        print(e)
        bot.reply_to(m, "Algo salio mal al obtener los valores")


def prepare(user, cid):
    try:
        if user.market in operatives:
            operatives[user.market]
        else:
            trader = TraderOPS()
            trader.monitor = CryptoBot(crypto=user.crypto, ref=user.pair,
                                       exchange='BINANCE')
            operatives[user.market] = trader
            send_message(cid, "Se ha preparado %s" % user.market)
    except:
        send_message(cid, "Error al preparar la operativa")


@bot.message_handler(commands=["configuracion"])
def my_settings(m):
    try:
        cid = m.chat.id
        bot.send_chat_action(cid, "typing")
        settings = get_settings(cid)
        send_message(cid, settings)
        user = get_user_info(cid)
        user.market = settings.current_market
        user.platform = settings.current_platform
        user.crypto = settings.current_crypto
        user.pair = settings.current_pair
        prepare(user, cid)
        save_user_info(cid, user)
    except Exception as e:
        print(e)
        bot.reply_to(m, "Algo salio mal al obtener tus datos")

from modules.financing.crypto.exchange_fn import current_stats, print_values, trade_mxn_btc
from bot.bot import bot
from modules.financing.data.user import Convertion, convertion_dict
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from decimal import Decimal


@bot.message_handler(commands=["btc_mxn"])
def btc_mxn(message):
    msg = bot.reply_to(
        message,
        "¿Cuál es la cantidad de BTC a convertir?",
    )
    bot.register_next_step_handler(msg, btc_mxn_ask_mxn_amount)


def btc_mxn_ask_mxn_amount(message):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        response = message.text
        if response.replace(".", "").isdigit():
            convert = Convertion(Decimal(response))
            convertion_dict[cid] = convert
            bot.send_message(cid, "Calculando para " + response + " BTC")
            markup = ReplyKeyboardMarkup(row_width=2)
            markup.add(
                KeyboardButton("Valor actual"), KeyboardButton("Valor personalizado")
            )
            msg = bot.reply_to(
                message,
                "¿Cómo quieres calcular la conversión de BTC?",
                reply_markup=markup,
            )
            bot.register_next_step_handler(msg, btc_mxn_process)
        else:
            bot.send_message(
                cid,
                "Debe ser un valor númerico, intente otra vez ejecutando el comando",
            )
    except Exception as e:
        print(e)
        bot.reply_to(message, "Algo salio mal al convertir")


def btc_mxn_process(message, market):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        response = message.text
        if response == "Valor actual":
            current_price = Decimal(current_stats(market)["ask"])
            convertion = convertion_dict[cid]
            convertion.price = current_price
            value = print_values(trade_mxn_btc(convertion.amount, convertion.price))
            bot.send_message(cid, "Tu resultado está listo:")
            bot.send_message(cid, value)
        else:
            msg = bot.reply_to(
                message, "¿Cuál es el valor de BTC con el que quieres hacer el cálculo?"
            )
            bot.register_next_step_handler(msg, btc_mxn_ask_btc_price)
    except Exception as e:
        print(e)
        bot.reply_to(message, "Algo salio mal al obtener los valores")


def btc_mxn_ask_btc_price(message):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        response = message.text
        if response.replace(".", "").isdigit():
            convertion = convertion_dict[cid]
            convertion.price = Decimal(response)
            value = print_values(trade_mxn_btc(convertion.amount, convertion.price))
            bot.send_message(cid, "Tu resultado está listo:")
            bot.send_message(cid, value)
        else:
            bot.send_message(
                cid,
                "Debe ser un valor númerico, intente otra vez ejecutando el comando",
            )
    except Exception as e:
        print(e)
        bot.reply_to(message, "Algo salio mal al obtener los valores")
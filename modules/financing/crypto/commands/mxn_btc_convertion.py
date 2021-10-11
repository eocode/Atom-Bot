from modules.financing.crypto.operations import current_stats, print_values, trade_btc
from bot.bot import bot
from modules.financing.data.user import Convertion, convertion_dict
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from decimal import Decimal
from modules.core.model.account import get_settings
from connect.communication import send_message


@bot.message_handler(commands=["crypto_convert_second_to_first"])
def crypto_convert_second_to_first(message):
    msg = bot.reply_to(
        message,
        "¿Cuál es la cantidad en pesos MXN a convertir?",
    )
    bot.register_next_step_handler(msg, cypto_convert_second_to_first_amount)


def cypto_convert_second_to_first_amount(message):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        response = message.text
        if response.replace(".", "").isdigit():
            convert = Convertion(Decimal(response))
            convertion_dict[cid] = convert
            send_message(cid, "Calculando para $" + response + " MXN")
            markup = ReplyKeyboardMarkup(row_width=2)
            markup.add(
                KeyboardButton("Valor actual"), KeyboardButton("Valor personalizado")
            )
            msg = bot.reply_to(
                message,
                "¿Cómo quieres calcular la conversión de BTC?",
                reply_markup=markup,
            )
            bot.register_next_step_handler(msg, cypto_convert_second_to_first_process)
        else:
            send_message(
                cid,
                "Debe ser un valor númerico, intente otra vez ejecutando el comando",
            )
    except Exception as e:
        print(e)
        bot.reply_to(message, "Algo salio mal al convertir")


def cypto_convert_second_to_first_process(message):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        response = message.text
        if response == "Valor actual":
            market = get_settings(cid).current_market
            current_price = Decimal(current_stats(market)["ask"])
            convertion = convertion_dict[cid]
            convertion.price = current_price
            value = print_values(trade_btc(convertion.amount, convertion.price))
            send_message(cid, "Tu resultado está listo:")
            send_message(cid, value)
        else:
            msg = bot.reply_to(
                message, "¿Cuál es el valor de BTC con el que quieres hacer el cálculo?"
            )
            bot.register_next_step_handler(msg, cypto_convert_second_to_first_price)
    except Exception as e:
        print(e)
        bot.reply_to(message, "Algo salio mal al obtener los valores")


def cypto_convert_second_to_first_price(message):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        response = message.text
        if response.replace(".", "").isdigit():
            convertion = convertion_dict[cid]
            convertion.price = Decimal(response)
            value = print_values(trade_btc(convertion.amount, convertion.price))
            send_message(cid, "Tu resultado está listo:")
            send_message(cid, value)
        else:
            send_message(
                cid,
                "Debe ser un valor númerico, intente otra vez ejecutando el comando",
            )
    except Exception as e:
        print(e)
        bot.reply_to(message, "Algo salio mal al obtener los valores")
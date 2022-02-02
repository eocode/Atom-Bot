from bot.bot import bot, commands
from connect.communication import send_voice, name, send_message, valid_user
from bot.constants import version
from modules.core.cognitive.greetings import get_greeting
from modules.core.model.account import update_settings

import unidecode
from modules.financing.connector.binance.trader import CryptoBot


@bot.message_handler(commands=["mi_identificador"])
def command_start(m):
    cid = m.chat.id
    send_message(cid, "Tú identificador es: " + str(cid))


@bot.message_handler(commands=["acerca_de_tu_bot"])
def command_start(m):
    cid = m.chat.id
    text = (
            "Hola "
            + m.chat.first_name
            + " soy "
            + name
            + " versión "
            + version
            + ", ¿En qué puedo ayudarte?"
    )
    send_message(
        cid,
        text + ", para conocer mis funcionalidades solo escribe /ayuda",
    )
    if valid_user(cid):
        send_voice(text)


@bot.message_handler(commands=["start"])
def command_start(m):
    cid = m.chat.id
    try:
        verified = valid_user(cid)
        if verified:
            text = (
                    "Genial! "
                    + m.chat.first_name
                    + ", tu cuenta ha sido verificada y tienes acceso a todas las funcionalidades, para ver todos los comandos presiona: /ayuda."
            )
        else:
            text = (
                    "Se ha creado tu cuenta! "
                    + m.chat.first_name
                    + ", pero, necesitas tener una cuenta verificada para acceder a las funcionaliades completas"
            )

        send_message(cid, text)
        update_settings(
            cid=cid, name=m.chat.first_name, current_market="btc_mxn", verified=verified
        )
        send_voice(
            "Se agregó la cuenta de: " + m.chat.first_name
        )
    except Exception as e:
        print(e)
        send_message(
            cid,
            "Ocurrio un error",
        )


@bot.message_handler(commands=["ayuda"])
def command_help(m):
    cid = m.chat.id
    help_text = "Puedo realizar las siguientes tareas: \n"
    for key in commands:
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    send_message(cid, help_text, play=False)


@bot.message_handler(func=lambda m: True)
def echo_message(m):
    cid = m.chat.id
    bot.send_chat_action(cid, "typing")
    text = unidecode.unidecode(m.text)
    if text.lower() == "hola":
        reply = get_greeting(m.chat.first_name)
        bot.reply_to(m, reply)
        send_voice(reply)
    else:
        if text.lower() == "di":
            msg = bot.reply_to(m, "¿Qué quieres que diga en el altavoz?")
            bot.register_next_step_handler(msg, say_something)
        else:
            if text.lower() == "ayuda":
                command_help(m)
                send_voice("Te acabo de enviar la lista de comandos")


def say_something(message):
    try:
        cid = message.chat.id
        response = message.text
        if valid_user(cid):
            text = "Reproduciendo"
            send_message(cid, text, play=False)
            send_voice(response)
        else:
            text = "Tú usuario no puede realizar está acción"
            send_message(cid, text)
    except Exception as e:
        print(e)
        bot.reply_to(message, "Algo salio mal")

from bot.bot import bot, knownUsers, commands, send_voice, name
from bot.constants import version
from modules.core.cognitive.greetings import get_greeting
from modules.core.model.account import update_settings

import unidecode


@bot.message_handler(commands=["mi_identificador"])
def command_start(m):
    cid = m.chat.id
    bot.send_message(cid, "Tú identificador es: " + str(cid))


@bot.message_handler(commands=["foto"])
def sed_photo(m):
    cid = m.chat.id
    bot.send_message(cid, "Te enviare los datos de BTC: ")
    bot.send_photo(cid, photo=open('btcusdt.png', 'rb'))


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
    bot.send_message(
        cid,
        text + ", para conocer mis funcionalidades solo escribe /ayuda",
    )
    if str(cid) in knownUsers:
        send_voice(text)


@bot.message_handler(commands=["start"])
def command_start(m):
    cid = m.chat.id
    try:
        verified = str(cid) in knownUsers
        print(verified)
        if verified:
            knownUsers.append(cid)
            text = (
                    "Genial! "
                    + m.chat.first_name
                    + ", tu cuenta ha sido verificada y tienes acceso a todas las funcionalidades, para ver todos los comandos presiona: /ayuda."
            )
        else:
            text = (
                    "Lo sentimos! "
                    + m.chat.first_name
                    + ", se ha creado tu cuenta, pero actualmente tienes funciones limitadas, solicita al administrador que te agregue como usuario verificado en el grupo del hogar"
            )

        bot.send_message(
            cid,
            text,
        )
        update_settings(
            cid=cid, name=m.chat.first_name, current_market="btc_mxn", verified=verified
        )
        send_voice(
            "Se agregó la cuenta de: " + m.chat.first_name + " al grupo del hogar"
        )
    except Exception as e:
        print(e)
        bot.send_message(
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
    bot.send_message(cid, help_text)


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
        if str(cid) in knownUsers:
            bot.send_chat_action(cid, "typing")
            text = "Reproduciendo"
            bot.send_message(
                cid,
                text,
            )
            send_voice(response)
        else:
            bot.send_chat_action(cid, "typing")
            text = "Tú usuario no puede realizar está acción"
            bot.send_message(
                cid,
                text,
            )
    except Exception as e:
        print(e)
        bot.reply_to(message, "Algo salio mal")

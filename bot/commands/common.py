from bot.bot import bot, knownUsers, commands, send_voice, name, version
from data.models.settings import update_settings
import random
import unidecode


@bot.message_handler(commands=["get_cid"])
def command_start(m):
    cid = m.chat.id
    bot.send_message(cid, "Tú CID es: " + str(cid))


@bot.message_handler(commands=["info"])
def command_start(m):
    cid = m.chat.id
    text = (
        "Hola "
        + m.chat.first_name
        + " mi nombre es: "
        + name
        + " y actualmente me encuentro en la versión "
        + version
    )
    bot.send_message(
        cid,
        text,
    )
    if str(cid) in knownUsers:
        send_voice(text)


@bot.message_handler(commands=["start"])
def command_start(m):
    cid = m.chat.id
    verified = str(cid) in knownUsers
    print(verified)
    if verified:
        knownUsers.append(cid)
        text = (
            "Genial! "
            + m.chat.first_name
            + ", tu cuenta ha sido verificada y tienes acceso a todas las funcionalidades, para ver todos los comandos presiona: /help."
        )
    else:
        text = "Lo sentimos! "
        +m.chat.first_name
        +", se ha creado tu cuenta, pero actualmente tienes funciones limitadas, solicita al administrador que te agregue como usuario verificado en el grupo del hogar"
    bot.send_message(
        cid,
        text,
    )
    update_settings(
        cid=cid, name=m.chat.first_name, current_market="btc_mxn", verified=verified
    )
    send_voice("Se agregó la cuenta de: " + m.chat.first_name + " al grupo del hogar")


@bot.message_handler(commands=["help"])
def command_help(m):
    cid = m.chat.id
    help_text = "Puedo realizar las siguientes tareas: \n"
    for key in commands:
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    cid = message.chat.id
    bot.send_chat_action(cid, "typing")
    text = unidecode.unidecode(message.text)
    if text.lower() == "hola":
        numberList = [
            "Hola " + message.chat.first_name + ", buen día",
            "Buen día",
            "Que tal",
            "Hola",
            "Hola, ¿estás list@ para comenzar?",
        ]
        bot.reply_to(message, random.choice(numberList))
    else:
        if text.isalpha():
            bot.reply_to(message, "Pruba con algún comando")
    command_help(message)
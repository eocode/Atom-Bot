from bot.bot import bot, knownUsers, commands
from bot.data.trade import userStep
import random
import unidecode

@bot.message_handler(commands=["start"])
def command_start(m):
    cid = m.chat.id
    if str(cid) not in knownUsers:
        knownUsers.append(cid)
        userStep[cid] = 0
        bot.send_message(
            cid,
            "Buen día! "
            + m.chat.first_name
            + ", bienvenido a trader bot pro by eocode, te puedo ayudar con tus operaciones de Trading.",
        )
        command_help(m)
    else:
        bot.send_message(
            cid, "Buen día! " + m.chat.first_name + ", ejecuta un comando para comenzar"
        )


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
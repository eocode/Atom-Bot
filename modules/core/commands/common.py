from bot.bot import bot
from bot.connect.message_connector import send_voice, name, send_message, get_chat_info
from bot.connect.resources_connector import get_monitor
from bot.constants import version
from modules.core.cognitive.greetings import get_greeting
from modules.core.model.account import update_settings
import unidecode

from modules.financing.crypto.data.dictionary import binance_order_books


@bot.message_handler(commands=["acerca"])
def command_start(m):
    user = get_chat_info(m)
    if not user.group['group']:
        text = (
                "Hola "
                + user.name
                + " soy "
                + name
                + " versión "
                + version
                + ", ¿En qué puedo ayudarte?"
        )
    else:
        text = (
                "Hola  grupo soy "
                + name
                + " versión "
                + version
                + ", la última actualización fue hace " + str(user.minutes)
                + " minutos. La reproducción está " + ("Activada" if user.speak else "Desactivada")
        )
    send_message(
        cid=user.cid,
        text=text,
        play=False
    )


@bot.message_handler(commands=["start"])
def command_start(m):
    user = get_chat_info(m)
    try:
        if user.is_active:
            if user.is_verified:
                if user.group['group']:
                    text = (
                            "Genial!, el grupo "
                            + user.name
                            + " está activado."
                    )
                else:
                    text = (
                            "Genial! "
                            + user.name
                            + ", tu cuenta ha sido verificada y tienes acceso a todas las funcionalidades, para ver todos los comandos presiona: /ayuda."
                    )
            else:
                text = (
                        user.name
                        + " tú cuenta es de uso limitado, tiene que adquirir una suscripción para acceder a todas las funcionalidades."
                )
        else:
            text = (
                    "Se ha creado tu cuenta! "
                    + user.name
                    + ", pero, necesitas tener una cuenta verificada para acceder a las funcionaliades completas"
            )
            send_voice(
                "Se agregó la cuenta de: " + user.name
            )
            update_settings(
                cid=user.cid, name=user.name, verified=user.is_verified, group=user.group['group']
            )
        send_message(user.cid, text)

    except Exception as e:
        print(e)
        send_message(
            user.cid,
            "Ocurrio un error",
        )


@bot.message_handler(commands=["ayuda"])
def command_help(m):
    user = get_chat_info(m)

    help_text = "Hola ... \n\n"
    help_text += "Como asistente puedo apoyarte a operar en el mercado crypto con algunas alertas para el mercado de futuros, solo pidelo"
    send_message(user.cid, help_text, play=False)


@bot.message_handler(commands=["alertas"])
def command_alerts(m):
    user = get_chat_info(m)

    if (not user.group['group'] and user.is_verified) or user.is_admin:
        for key, value in binance_order_books.items():
            get_monitor(value['crypto'] + value['pair']).show_operative()
    else:
        send_message(user.cid, "Operación inválida")


@bot.message_handler(commands=["resultados"])
def command_results(m):
    for key, value in binance_order_books.items():
        get_monitor(value['crypto'] + value['pair']).show_stats()


@bot.message_handler(func=lambda m: True)
def echo_message(m):
    user = get_chat_info(m)
    bot.send_chat_action(user.cid, "typing")
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
            else:
                if text.lower() == "alertas":
                    command_alerts(m)
                else:
                    if text.lower() == "resultados":
                        command_results(m)


@bot.message_handler(commands=["alertas"])
def command_operation(m):
    for key, value in binance_order_books.items():
        get_monitor(value['crypto'] + value['pair']).show_operative()


# @bot.message_handler(commands=["ver_graficos"])
# def command_operation(m):
#     user = get_chat_info(m)
#     if user.market in operatives:
#         operatives[user.market].monitor.get_market_graphs(bot, user.cid)
#     else:
#         send_message(user.cid, 'Necesita preparar la operativa antes')


def say_something(m):
    try:
        user = get_chat_info(m)
        response = m.text
        if user.is_verified:
            text = "Reproduciendo"
            print(user.cid, text)
            send_message(cid=user.cid, text=text, play=False)
            send_voice(response)
        else:
            text = "Tú usuario no puede realizar está acción"
            send_message(cid=user.cid, text=text)
    except Exception as e:
        print(e)
        bot.reply_to(m, "Algo salio mal")

from bot.bot import bot, commands
from bot.connect.message_connector import send_voice, name, send_message, get_chat_info
from bot.constants import version
from modules.core.cognitive.greetings import get_greeting
from modules.core.model.account import update_settings
import unidecode

from modules.financing.data.operative import start_operatives


@bot.message_handler(commands=["acerca"])
def command_start(m):
    cid, verified, chat_name, group, admin, active = get_chat_info(m)
    text = (
            "Hola "
            + chat_name
            + " soy "
            + name
            + " versión "
            + version
            + ", ¿En qué puedo ayudarte?"
    )
    send_message(
        cid,
        text
    )


@bot.message_handler(commands=["start"])
def command_start(m):
    cid, verified, chat_name, group, admin, active = get_chat_info(m)
    try:
        if active:
            if verified:
                if group['group']:
                    text = (
                            "Genial! "
                            + chat_name
                            + ", el grupo está activado."
                    )
                else:
                    text = (
                            "Genial! "
                            + chat_name
                            + ", tu cuenta ha sido verificada y tienes acceso a todas las funcionalidades, para ver todos los comandos presiona: /ayuda."
                    )
            else:
                text = (
                        "Falta poco! "
                        + chat_name
                        + ", ahora solo se tiene que verificar la cuenta para acceder a todas las funcionalidades."
                )
        else:
            text = (
                    "Se ha creado tu cuenta! "
                    + chat_name
                    + ", pero, necesitas tener una cuenta verificada para acceder a las funcionaliades completas"
            )
            send_voice(
                "Se agregó la cuenta de: " + chat_name
            )
            update_settings(
                cid=cid, name=chat_name, verified=verified, group=group['group']
            )
        send_message(cid, text)

    except Exception as e:
        print(e)
        send_message(
            cid,
            "Ocurrio un error",
        )


@bot.message_handler(commands=["ayuda"])
def command_help(m):
    cid, verified, chat_name, group, admin, active = get_chat_info(m)

    help_text = "Soy %s, tú asistente personal. Puedo ayudarte a realizar operaciones en el mercado crypto ... \n\n" % \
                name
    help_text += "Te comparto los siguientes comandos: \n\n"
    for key in commands:
        if key not in ("ayuda", "start"):
            if key not in ("simular_trades", "elegir_mercado", "ver_graficos", "ver_analisis", "ver_resumen", "trade",
                           "trade_actual") or verified and not group['group']:
                if key not in ("simular_trades", "trade") or admin and not group['group']:
                    help_text += "/" + key + ": "
                    help_text += commands[key] + "\n"
    send_message(cid, help_text, play=False)


@bot.message_handler(func=lambda m: True)
def echo_message(m):
    cid, verified, chat_name, group, admin, active = get_chat_info(m)
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
            else:
                if text.lower() == "iniciar":
                    if group['group']:
                        if group['is_admin']:
                            send_message(cid, "Analizando mercado con la version %s" % version)
                            start_operatives(cid)
                        else:
                            send_message(cid, "No tiene permiso de ejecutar está opción")
                    else:
                        send_message(cid, "Solo se permite usar en grupos")
                else:
                    send_message(cid, "No entendí")


def say_something(m):
    try:
        cid, verified, chat_name, group, admin, active = get_chat_info(m)
        response = m.text
        if verified:
            text = "Reproduciendo"
            print(cid, text)
            send_message(cid=cid, text=text, play=False)
            send_voice(response)
        else:
            text = "Tú usuario no puede realizar está acción"
            send_message(cid=cid, text=text)
    except Exception as e:
        print(e)
        bot.reply_to(m, "Algo salio mal")

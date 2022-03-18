from bot.bot import bot, commands
from bot.connect.message_connector import send_voice, name, send_message, get_chat_info
from bot.constants import version
from modules.core.cognitive.greetings import get_greeting
from modules.core.model.account import update_settings
import unidecode

from modules.financing.data.operative import start_operatives


@bot.message_handler(commands=["acerca"])
def command_start(m):
    user = get_chat_info(m)
    if not user.group['group']:
        text = (
                "Hola grupo "
                + user.name
                + " soy "
                + name
                + " versión "
                + version
                + ", ¿En qué puedo ayudarte?"
        )
    else:
        text = (
                "Hola "
                + user.name
                + " soy "
                + name
                + " versión "
                + version
                + ", la última sync fue hace " + str(user.minutes)
                + " y la reproducción está " + ("Activada" if user.speak else "Desactivada")
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
                        "Falta poco! "
                        + user.name
                        + ", ahora solo se tiene que verificar la cuenta para acceder a todas las funcionalidades."
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

    help_text = "Puedo ayudarte a realizar operaciones en el mercado crypto ... \n\n"
    help_text += "Te comparto los siguientes comandos: \n\n"
    for key in commands:
        if key not in ("ayuda", "start"):
            if key not in (
                    "simular_trades", "elegir_mercado", "ver_graficos", "trade") or user.is_verified and not \
                    user.group['group']:
                if key not in ("simular_trades", "trade") or user.is_admin and not user.group['group']:
                    if key not in ("alertas") or user.is_verified:
                        help_text += "/" + key + ": "
                        help_text += commands[key] + "\n"
    send_message(user.cid, help_text, play=False)


@bot.message_handler(commands=["iniciar"])
def command_init(m):
    user = get_chat_info(m)

    if user.group['group']:
        if user.group['is_admin']:
            send_message(user.cid, "Analizando con la versión %s" % version, play=False)
            start_operatives(user.cid)
        else:
            send_message(user.cid, "No tiene permiso de ejecutar está opción")
    else:
        send_message(user.cid, "Solo se permite usar en grupos")


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
                if text.lower() == "iniciar":
                    command_init(m)


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

from gtts import gTTS
import hashlib
from platform import system
import os

from telebot.types import ReplyKeyboardRemove

from bot.connect.thread_connector import async_fn, limit
from bot.constants import version
from bot.bot import bot
from modules.core.data.user import get_user_info
from modules.core.model.account import get_settings
import subprocess

name = os.environ["bot_name"]
thisOS = system()


def get_chat_info(m):
    cid = m.chat.id
    print(m.chat.type)
    usr = get_settings(cid)
    if usr is not None:
        verified = usr.is_verified
        is_admin = usr.is_admin
        is_active = True
    else:
        verified = False
        is_admin = False
        is_active = False
    if m.chat.type in ("group", "supergroup"):
        chat_name = m.chat.title
        usr2 = get_settings(m.from_user.id)
        if usr2 is not None:
            verified2 = usr2.is_verified
            is_admin2 = usr2.is_admin
            is_active2 = True
        else:
            verified2 = False
            is_admin2 = False
            is_active2 = False
        group = {"cid": m.from_user.id, "name": m.from_user.first_name, "group": True, "verified": verified2,
                 "is_admin": is_admin2, "is_active": is_active2}
    else:
        chat_name = m.chat.first_name
        group = {"group": False}
    return cid, verified, chat_name, group, is_admin, is_active


@limit(10)
@async_fn
def send_voice(text):
    file = hashlib.md5(text.encode()).hexdigest() + ".mp3"
    if thisOS == "Linux":
        tts = gTTS(text, lang="es", tld="com.mx")
        tts.save(file)
        subprocess.run("mpg123 " + file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    else:
        tts = gTTS(text, lang="es", tld="com.mx")
        tts.save(file)
        from playsound import playsound
        playsound(file)
    os.remove(file)


def send_message(cid, text, play=True, close_markup=False):
    usr = get_user_info(cid)
    bot.send_chat_action(cid, "typing")
    if close_markup:
        bot.send_message(
            cid,
            text,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        bot.send_message(
            cid,
            text
        )
    if usr.speak and play:
        send_voice(text)


def send_photo(cid, photo):
    bot.send_photo(cid, photo=open(photo, 'rb'))


@limit(10)
@async_fn
def say_hello(init_type="init"):
    if init_type == "init":
        send_voice("Iniciando ... " + name)
    if init_type == "update":
        send_voice(name + " " + version)

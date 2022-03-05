from gtts import gTTS
import hashlib
from platform import system
import os

from telebot.types import ReplyKeyboardRemove

from bot.constants import version
from bot.bot import bot
from modules.core.data.user import get_user_info
from modules.core.model.account import get_settings

name = os.environ["bot_name"]
thisOS = system()


def valid_user(cid):
    usr = get_settings(cid)
    if usr is None:
        return False
    else:
        return usr.is_verified


def send_voice(text):
    file = hashlib.md5(text.encode()).hexdigest() + ".mp3"
    if thisOS == "Linux":
        tts = gTTS(text, lang="es", tld="com.mx")
        tts.save(file)
        os.system("mpg123 " + file)
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
    if usr is not None:
        if usr.speak and play:
            send_voice(text)


def send_photo(cid, photo):
    print(photo)
    bot.send_photo(cid, photo=open(photo, 'rb'))


def say_hello(init_type="init"):
    if init_type == "init":
        send_voice("Iniciando ... " + name)
    if init_type == "update":
        send_voice(name + " " + version)

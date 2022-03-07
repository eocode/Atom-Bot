from gtts import gTTS
import hashlib
from platform import system
import os

from telebot.types import ReplyKeyboardRemove

from bot.connect.thread_connector import async_fn, limit
from bot.constants import version
from bot.bot import bot
from modules.core.data.user import get_user_info, load_user
import subprocess

name = os.environ["bot_name"]
thisOS = system()


def get_chat_info(m):
    usr = load_user(m)
    return usr


@limit(10)
@async_fn
def send_voice(text):
    file = hashlib.md5(text.encode()).hexdigest() + ".wav"
    tts = gTTS(text, lang="es", tld="com.mx")
    tts.save(file)
    if thisOS == "Linux":
        subprocess.run("mpg123 " + file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    else:
        subprocess.run("ffplay %s -autoexit -nodisp" + file, shell=True, stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL)
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

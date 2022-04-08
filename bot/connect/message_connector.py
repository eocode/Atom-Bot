import requests
from gtts import gTTS
import hashlib
from platform import system
import os

from telebot.types import ReplyKeyboardRemove

from bot.connect.thread_connector import async_fn, limit
from bot.constants import version
from bot.bot import bot
from modules.core.data.user import get_user_info, load_user
import random
import subprocess

name = os.environ["bot_name"]
thisOS = system()


def get_chat_info(m):
    usr = load_user(m)
    return usr


def send_voice(text):
    file = hashlib.md5(text.encode()).hexdigest() + str(random.randint(1, 100000)) + ".wav"
    tts = gTTS(text, lang="es", tld="com.mx")
    tts.save(file)
    if thisOS == "Linux":
        subprocess.run("mpg123 " + file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    else:
        subprocess.run("ffplay %s -autoexit -nodisp" % file, shell=True, stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL)
    os.remove(file)


def logging_message(text):
    print(text)


def bot_message(close_markup, cid, text):
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


def send_messsage_by_rest(cid, text):
    message = "https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" % (os.environ["telegram_token_bot"], cid, text)
    res = requests.get(message)
    print(res.text)
    print(res.status_code)


def send_message(cid, text, play=True, close_markup=False):
    usr = get_user_info(cid)
    print('Show message ', usr.speak, play, cid)
    bot.send_chat_action(cid, "typing")
    try:
        bot_message(close_markup, cid, text)
        if usr.speak and play:
            print('Send to speaker')
            send_voice(text)
    except Exception as e:
        bot_message(close_markup, cid, text)
        print(e)


def send_photo(cid, photo):
    bot.send_photo(cid, photo=open(photo, 'rb'))


@limit(10)
@async_fn
def say_hello(init_type="init"):
    if init_type == "init":
        send_voice("Iniciando ... " + name)
    if init_type == "update":
        send_voice(name + " " + version)


def send_initial_message(chat_id, text):
    bot_message(close_markup=False, cid=chat_id, text=text)

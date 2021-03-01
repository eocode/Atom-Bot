import random
from datetime import datetime


def get_hour():
    return datetime.now().hour


def get_greeting(user):

    words = ["Hola", "Buen día!"]

    hour = get_hour()

    if hour >= 0  and hour < 5:
       words.append("¡Hola " + user + ", deberías de estár durmiendo a estas horas!")

    if hour >= 5 and hour < 12:
        words.append("¡Hola " + user + ", que tengas un buen día!")
        words.append("Buenos días " + user)
        words.append("Hola " + user)
        words.append("Hola, buen día " + user)

    if hour >= 12 and hour < 19:
        words.append("Hola " + user)
        words.append("Buenas tardes " + user)
        words.append("Qué tal " + user)        

    if hour >= 19 and hour < 22:
        words.append("Buenas noches " + user)

    if hour >= 22 and hour <= 24:
        words.append("Hola, ha sido un día pesado " + user)
        words.append("Hola, ya casi es hora de ir a dormir " + user)

    return random.choice(words)
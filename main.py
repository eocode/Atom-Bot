# Load DB configuration
from data.db import Base, engine

# Load arthur
from bot.bot import bot, init, say_hello

# Load all available commands
from bot.commands import *

# Load time
import time

if __name__ == "__main__":
    # DB init
    Base.metadata.create_all(engine)
    # Init Bot
    init(bot)

    # Bot settings
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()

    say_hello()

    while 1:
        try:
            # Show user message
            print("Server started")
            # Run the bot
            bot.polling()
            # Sleep 5
            time.sleep(5)
        except:
            print("Error")
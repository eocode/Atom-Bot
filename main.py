# Load DB configuration
from bot.brain import Base, engine

# Load arthur
from bot.bot import init, say_hello

# Load all available commands with modules
from bot import *

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
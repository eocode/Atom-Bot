# Load DB configuration
from bot.brain import Base, engine
from bot.connect.communication import say_hello
import sys

# Load arthur
from bot.bot import init

# Load all available commands with modules
from bot import *

# Load time
import time

if __name__ == "__main__":
    args = sys.argv
    args.pop(0)

    say = "init"

    if len(args) > 0:
        say = "update"

    # DB init
    Base.metadata.create_all(engine)
    # Init Bot
    init(bot)

    # Bot settings
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()

    say_hello(say)

    while 1:
        try:
            # Show user message
            print("Server started")
            # Run the bot
            bot.polling()
            # Sleep 5
            time.sleep(5)
        except Exception as e:
            print("Error:", e)

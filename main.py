# Load DB configuration
from bot.connect.message_connector import say_hello
import sys

# Load arthur
from bot.bot import init

# Load all available commands with modules
from bot import *

from modules.financing.data.operative import initialize_operatives

if __name__ == "__main__":
    args = sys.argv
    args.pop(0)

    say = "init"

    if len(args) > 0:
        say = "update"

    # Init Bot
    init(bot)

    # Bot settings
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()

    say_hello(say)

    try:
        # Configure initial data
        initialize_operatives()

        # Show user message
        print("Server started")
        # Run the bot
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print("Error:", e)

# Ada

A simple bot with a crypto module in bitso

<div align="center">
    <img src="img/bot.png" 
    alt="visitors"/>
</div>

## Features
* Bitso API
  * Smart alerts
  * Commission calculation
  * Simulations
  * Monitors
* Telegram messages by users
* Speak messages
* RaspberryPI compatibility connected by bluetoth with Alexa

### Require

* Python 3.7 +

### Install

``pip install -r requirements.txt``

``python arthur.py``

#### Env file

In root directory create a .env file with:

```
# MySQL Credentials
DB_USER='your user'
DB_PASS='your pass'
DB_NAME='your name'
DB_HOST='your host'

# Telegram access
telegram_users = 'string separated with comma' 
telegram_token_bot = 'your token'
bot_name = 'bot_name'
bot_version = "bot_version"
```
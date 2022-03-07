<div align="center">
  <div align="center">
      <img width="100px" src="https://github.com/eocode/Atom-Bot/raw/main/bot/img/logo.png" 
      alt="Atom"/>
  </div>
  <h3 align="center">Atom (Assistant)</h3>
  <p>A simple bot with a finance module</p>
  <p align="center">
    <a href="https://github.com/eocode/Queens/blob/master/LICENSE" target="__blank">
      	<img src="https://img.shields.io/badge/License-GPLV3-blue.svg"  alt="license badge"/>
    </a>
    <a href="https://github.com/ambv/black" target="__blank">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" />
    </a>
    <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/eocode/Atom-Bot">
  </p>
</div>

## Features
* Binance (USDT)
  * Smart alerts and monitor
  * Market Analyze
  * Graphs
  * Simulations and backtesting
* Telegram messages by users and groups
* Speak messages
* RaspberryPI compatibility connected by bluetooth with Alexa

### Require

* Python 3.7 +
* RaspberryPi 3 + - TriggerCMD for automated tasks and syncs
* MySQL Server
* Alexa
* Telegram Bot
* Static IP and Router configuration

## Support

* Linux
* Windows

## Architecture

<div align="center">
    <img src="https://github.com/eocode/Atom-Bot/raw/main/bot/img/architecture_updated.png" 
    alt="ada architecture"/>
</div>

### Install and run

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

# Bot settings
bot_name = 'bot_name'
```

In root, rename alembic_conf.ini and update sqlalchemy.url

``change to alembic.ini``

Install dependencies

``pip install -r requirements.txt``

For ubuntu requiere
``sudo apt-get update``

``sudo apt-get install mpg123``

For windows requiere

`Install https://ffmpeg.org and add to path`

Migrations

``alembic revision --autogenerate -m "first migration"``

``alembic upgrade head``

Run program

``python main.py``

## Contribution

Contribute to make the best virtual assistant bot for raspberry pi and python

* Contact me @eocode in social media
* See the issue list
* Clone this project and add your contributions
* Send me a pull request

## LICENSE 

GNU GENERAL PUBLIC LICENSE

Version 3, 29 June 2007

https://github.com/eocode/Atom-Bot/blob/main/LICENSE
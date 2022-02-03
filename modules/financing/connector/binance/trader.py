import math

import pandas as pd
from binance.exceptions import BinanceAPIException

from connect.communication import send_message
from modules.financing.connector.binance.extractor import get_binance_symbol_data, save_extracted_data, symbol_info, \
    get_file_name
from modules.financing.connector.binance.order_management import create_order
from modules.financing.connector.binance.processing import analysis, plot_df, supres
from modules.financing.connector.binance.configuration import configuration, trades
from time import sleep
import json
import numpy as np


class CryptoBot:

    def __init__(self, binance_client, crypto, ref, exchange='BINANCE'):
        self.client = binance_client
        self.symbol = crypto + ref
        self.crypto = crypto
        self.ref = ref
        self.exchange = exchange
        # Default Values
        self.max_min = None
        self.order_status = None
        self.order = None
        self.symbol_info = None
        self.update_symbol_info()
        self.configuration = configuration
        self.trades = trades
        self.process_is_started = False
        self.first_iteration = False

    def get_market_graphs(self, bot=None, cid=None):

        for time, options in self.configuration.items():
            try:
                # Get Data
                print(time)
                data = get_binance_symbol_data(symbol=self.symbol, kline_size=time, auto_increment=False,
                                               save=True, sma=options['days'])
                # Analyse
                options['data'] = analysis(df=data, ma_f=options['sma_f'], ma_s=options['sma_s'],
                                           mas=options['smas'], time=time)
                # options['min_max'] = get_stats(df=self.data)
                df = options['data'].tail(120)
                options['support'], options['resistance'] = supres(df['close'].to_numpy(), 30)
                save_extracted_data(symbol=self.symbol, df=options['data'], form='sma-%s' % options['days'], size=time)
                print('Plotting')
                # Visualize data

                plot_df(values=options['plot'], size=time, form='sma-%s' % options['days'],
                        symbol=self.symbol, support=options['support'], resistence=options['resistance'],
                        smas=options['smas'])

                # Send results
                photo = open(get_file_name(self.symbol, time, 'sma-%s' % options['days'], 'png'), 'rb')
                if bot is not None:
                    send_message(cid, time, play=False)
                    bot.send_photo(cid, photo)
            except Exception as e:
                print('Error PLOT: ', e)

    def start(self, cid=None):
        if not self.process_is_started:
            send_message(cid, "Iniciando monitoreo de trades", play=True)
            self.process_is_started = True
            while (True):
                # For all temps
                try:
                    for time, options in self.configuration.items():
                        # Get Data
                        data = get_binance_symbol_data(symbol=self.symbol, kline_size=time, auto_increment=False,
                                                       save=False, sma=options['days'])
                        # Analyse
                        options['data'] = analysis(df=data, ma_f=options['sma_f'], ma_s=options['sma_s'],
                                                   mas=options['smas'], time=time)
                        df = options['data'].tail(365)
                        options['support'], options['resistance'] = supres(df['close'].to_numpy(), 30)

                        last_row = df.iloc[-1, :]
                        self.take_decision(last_row, cid, time, options['support'], options['resistance'], False)
                        sleep(2.5)
                    self.first_iteration = True
                except Exception as e:
                    print('Error: ', e)
        else:
            send_message(cid, "Monitoreo iniciado", play=True)
            print('Ya se ha iniciado el proceso')

    def get_resume(self, type, mayor, menor, cid=None):
        long = False
        short = False
        message = ''
        message += type.upper() + " \n"

        if self.trades[type][mayor]['sell']:
            message += "Mercado a la baja "
            if self.trades[type][mayor]['sell_confirmation']:
                message += "confirmado\n"
            else:
                message += "sin confirmar\n"

            if self.trades[type][menor]['buy']:
                long = True
                # Venta y compra -> Rebote
                message += "Con Rebote alcista "
                if self.trades[type][menor]['buy_confirmation']:
                    message += "confirmado\n"
                else:
                    message += "sin confirmar\n"
            else:
                short = True
                # Venta y Venta -> Fuerza a la baja
                message += "Fuerza bajista "
                if self.trades[type][menor]['sell_confirmation'] and self.trades[type][mayor]['sell_confirmation']:
                    message += "confirmado\n"
                else:
                    message += "sin confirmar\n"

        if self.trades[type][mayor]['buy']:
            message += "Mercado a la alza "
            if self.trades[type][mayor]['buy_confirmation']:
                message += "confirmado\n"
            else:
                message += "sin confirmar\n"

            if self.trades[type][menor]['buy']:
                long = True
                # Compra y Compra -> Fuerza al alza
                message += "Tendencia fuerte al alza "
                if self.trades[menor][menor]['buy_confirmation']:
                    message += "confirmado\n"
                else:
                    message += "sin confirmar\n"
            else:
                short = True
                # Compra y Venta -> Corrección
                message += "Corrección "
                if self.trades[type][menor]['sell_confirmation']:
                    message += "confirmado\n"
                else:
                    message += "sin confirmar\n"

        if cid is not None:
            if long:
                message += '\nCOMPRA\n'
            if short:
                message += '\nVENTA\n'
            message += 'High: ' + str(self.trades[type][mayor]['trade']['high']) + ' Low: ' + \
                       str(self.trades[type][mayor]['trade']['low']) + ' Close: ' + str(self.trades[type][mayor]['trade'][
                           'close']) + '\n'
            message += 'RSI: ' + str(self.trades[type][mayor]['trade']['RSI']) + ' ' + str(self.trades[type][mayor]['trade']['RSIs']) + ' Momentum: ' + \
                       str(self.trades[type][mayor]['trade']['Momentum']) + ' ' + str(self.trades[type][mayor]['trade']['Momentums']) + '\n'
            send_message(cid, message)

        return long, short

    def get_trades(self, cid):
        self.show_dict(self.trades['large'], cid, False)
        self.show_dict(self.trades['medium'], cid, False)
        self.show_dict(self.trades['short'], cid, False)
        self.show_dict(self.trades['micro'], cid, False)

    def take_decision(self, last_row, cid, time, support, resistance, play):
        trade = self.market_sentiment(last_row, time, support, resistance)
        # if trade and self.first_iteration:
        #     self.show_message(time, cid, False)
        #     self.show_dict(self.trades[self.get_type_trade(time)][time], cid, False)

    def filter_operative(self, time):
        if time in ('1w'):
            return True

    def market_sentiment(self, last_row, time, support, resistance):
        trade = False
        if last_row['buy_trend']:
            trade = True
        else:
            if last_row['buy_confirmation'] and time not in ('1w'):
                trade = True

        if last_row['sell_trend']:
            trade = True
        else:
            if last_row['sell_confirmation'] and time not in ('1w'):
                trade = True

        trade = self.save_trade(time, last_row, trade, support, resistance)

        return trade

    def get_type_trade(self, time):
        type = ''
        if time in self.trades['large']:
            type = 'large'
        if time in self.trades['medium']:
            type = 'medium'
        if time in self.trades['short']:
            type = 'short'
        if time in self.trades['micro']:
            type = 'micro'

        return type

    def save_trade(self, time, last_row, trade, support, resistance):
        # Fingerprint
        fingerprint = last_row['time']

        type = self.get_type_trade(time)

        if self.trades[type][time]['fingerprint'] == fingerprint and trade:
            print('Es igual')
            return False
        else:
            print('No es igual')
            self.trades[type][time]['fingerprint'] = last_row['time']
            self.trades[type][time]['trend'] = last_row['trend']
            self.trades[type][time]['buy'] = last_row['buy_trend']
            self.trades[type][time]['sell'] = last_row['sell_trend']
            self.trades[type][time]['buy_confirmation'] = last_row['buy_confirmation']
            self.trades[type][time]['sell_confirmation'] = last_row['sell_confirmation']
            self.trades[type][time]['support'] = support
            self.trades[type][time]['resistance'] = resistance
            self.trades[type][time]['trade']['high'] = last_row['high']
            self.trades[type][time]['trade']['low'] = last_row['low']
            self.trades[type][time]['trade']['close'] = last_row['close']
            self.trades[type][time]['trade']['RSI'] = last_row['positive_momentum']
            self.trades[type][time]['trade']['RSIs'] = last_row['RSI_ups']
            self.trades[type][time]['trade']['Momentum'] = last_row['positive_RSI']
            self.trades[type][time]['trade']['Momentums'] = last_row['momentum_ups']
            return True

    def show_message(self, message, cid, play):
        if cid is not None:
            send_message(cid, message, play=play)
        else:
            print(message)

    def show_dict(self, dict, cid, play):
        s = json.dumps(dict, cls=CustomJSONizer, indent=4, sort_keys=False, default=str)
        if cid is not None:
            send_message(cid, s, play=play)
        else:
            print(s)

    def listToString(self, s):
        # initialize an empty string
        str1 = ""

        # traverse in the string
        for ele in s:
            str1 += str(ele) + ", "

            # return string
        return str1[:-2]

    def update_symbol_info(self):
        self.symbol_info = symbol_info(crypto=self.crypto, ref=self.ref, exchange=self.exchange)

    def log(self):
        """Crypto activity"""
        pass

    def run(self):
        pass

    def order(self, operation, quantity, price):
        """Sell and buys"""

        try:
            self.order = create_order(symbol=self.symbol, quantity=quantity, price=price, operation=operation)

        except BinanceAPIException as e:
            print(e)

        pass


class CustomJSONizer(json.JSONEncoder):
    def default(self, obj):
        return super().encode(bool(obj)) \
            if isinstance(obj, np.bool_) \
            else super().default(obj)

from binance.exceptions import BinanceAPIException

from bot.brain import binance_client
from bot.connect.communication import send_message
from modules.financing.connector.binance.extractor import get_binance_symbol_data, save_extracted_data, symbol_info, \
    get_file_name
from modules.financing.connector.binance.order_management import create_order
from modules.financing.connector.binance.processing import analysis, plot_df, supres
from modules.financing.connector.binance.configuration import configuration, trades
from time import sleep
import json
import numpy as np


class CryptoBot:

    def __init__(self, crypto, ref, exchange='BINANCE'):
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
                print(len(data.index))
                # Analyse
                options['data'] = analysis(df=data, ma_f=options['sma_f'], ma_s=options['sma_s'],
                                           mas=options['smas'], time=time)
                print(len(options['data'].index))
                save_extracted_data(symbol=self.symbol, df=options['data'], form='sma-%s' % options['days'], size=time)
                print('Analized')
                # options['min_max'] = get_stats(df=self.data)
                df = options['data'].tail(120)
                if len(df.index) > options['plot']:
                    options['support'], options['resistance'] = supres(df['close'].to_numpy(), options['plot'])
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
                                                       save=False, sma=options['days_s'])
                        # Analyse
                        options['data'] = analysis(df=data, ma_f=options['sma_f'], ma_s=options['sma_s'],
                                                   mas=options['smas'], time=time)
                        df = options['data'].tail(365)
                        options['support'], options['resistance'] = supres(df['close'].to_numpy(), 30)

                        last_row = df.iloc[-1, :]
                        self.market_sentiment(last_row, time, options['support'], options['resistance'])
                        sleep(2)
                    self.first_iteration = True
                    self.take_decision(cid, False)
                except Exception as e:
                    print('Error: ', e)
        else:
            send_message(cid, "Monitoreo iniciado", play=True)
            print('Ya se ha iniciado el proceso')

    def take_decision(self, cid, play=False):
        # Micro Trade
        if self.trades['micro']['1m']['trade']['Momentum'] == True and self.trades['micro']['1m']['trade'][
            'time'] == False and self.trades['micro']['5m']['trade']['Momentum'] == True and \
                self.trades['micro']['5m']['trade']['time'] == False:
            self.show_message(message='Micro Long', cid=cid, play=play)
            self.get_resume('micro', '5m', '1m', cid)
        if self.trades['micro']['1m']['trade']['Momentum'] == False and self.trades['micro']['1m']['trade'][
            'time'] == True and self.trades['micro']['5m']['trade']['Momentum'] == False and \
                self.trades['micro']['5m']['trade']['time'] == True:
            self.show_message(message='Micro Short', cid=cid, play=play)
            self.get_resume('micro', '5m', '1m', cid)

    def get_full_resumes(self, cid):
        if self.process_is_started and self.first_iteration:
            self.get_resume('large', '1w', '1d', cid)
            self.get_resume('medium', '4h', '1h', cid)
            self.get_resume('short', '30m', '15m', cid)
            self.get_resume('micro', '5m', '1m', cid)
        else:
            send_message(cid, "El reporte aún no está listo")

    def get_resume(self, type, mayor, menor, cid=None):

        long = False
        short = False
        message = ''

        if self.trades[type][mayor]['sell']:
            message += mayor.upper() + " 🔴 "
            if self.trades[type][mayor]['sell_confirmation']:
                message += "🔱 "
            else:
                message += "📛 "
            if self.trades[type][menor]['buy']:
                long = True
                # Venta y compra -> Rebote
                message += menor.upper() + " 🟢 Rebote alcista "
                if self.trades[type][menor]['buy_confirmation']:
                    message += "🔱 "
                else:
                    message += "📛 "
            else:
                short = True
                # Venta y Venta -> Fuerza a la baja
                message += menor.upper() + " 🔴 Fuerza bajista "
                if self.trades[type][menor]['sell_confirmation'] and self.trades[type][mayor]['sell_confirmation']:
                    message += "🔱 "
                else:
                    message += "📛 "

        if self.trades[type][mayor]['buy']:
            message += mayor.upper() + " 🟢 Alza "
            if self.trades[type][mayor]['buy_confirmation']:
                message += "🔱 "
            else:
                message += "📛 "

            if self.trades[type][menor]['buy']:
                long = True
                # Compra y Compra -> Fuerza al alza
                message += menor.upper() + " 🟢 Fuerza alcista "
                if self.trades[type][menor]['buy_confirmation']:
                    message += "🔱 "
                else:
                    message += "📛 "
            else:
                short = True
                # Compra y Venta -> Corrección
                message += menor.upper() + " 🔴 Corrección "
                if self.trades[type][menor]['sell_confirmation']:
                    message += "🔱 "
                else:
                    message += "📛 "

        message += '\n'

        if cid is not None:
            if long:
                message += '\n🟢 '
            if short:
                message += '\n🔴 '
            message += '🔼 ' + str(self.trades[type][mayor]['trade']['high']) + ' 🔽 ' + \
                       str(self.trades[type][mayor]['trade']['low']) + ' ⏺️ ' + str(
                self.trades[type][mayor]['trade'][
                    'close']) + '\n'
            message += mayor.upper() + ' RSI: ' + (
                '🟢' if self.trades[type][mayor]['trade']['RSI'] else '🔴') + ' ' + str(
                self.trades[type][mayor]['trade']['RSIs'])
            message += ' Momentum: ' + (
                '🟢' if self.trades[type][mayor]['trade']['Momentum'] else '🔴') + ' ' + (
                           '🔼' if self.trades[type][mayor]['trade']['time'] else '🔽') + ' ' + str(
                self.trades[type][mayor]['trade']['Momentums']) + '\n'
            message += menor.upper() + ' RSI: ' + (
                '🟢' if self.trades[type][menor]['trade']['RSI'] else '🔴') + ' ' + str(
                self.trades[type][menor]['trade']['RSIs'])
            message += ' Momentum: ' + (
                '🟢' if self.trades[type][menor]['trade']['Momentum'] else '🔴') + ' ' + (
                           '🔼' if self.trades[type][menor]['trade']['time'] else '🔽') + ' ' + str(
                self.trades[type][menor]['trade']['Momentums']) + '\n'
            message += 'Ema Sup: ' + (
                '🟢 ' if self.trades[type][mayor]['trade']['ema'] else '🔴 ') + str(
                round(self.trades[type][mayor]['trade']['ema_value'], 2)) + ' \n'
            message += 'Ema Inf: ' + (
                '🟢 ' if self.trades[type][menor]['trade']['ema'] else '🔴 ') + str(
                round(self.trades[type][menor]['trade']['ema_value'], 2)) + '\n'
            send_message(cid, message)

        return long, short

    def get_trades(self, cid):
        self.show_dict(self.trades['large'], cid, False)
        self.show_dict(self.trades['medium'], cid, False)
        self.show_dict(self.trades['short'], cid, False)
        self.show_dict(self.trades['micro'], cid, False)

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
            self.trades[type][time]['trade']['RSI'] = last_row['positive_RSI']
            self.trades[type][time]['trade']['RSIs'] = last_row['RSI_ups']
            self.trades[type][time]['trade']['Momentum'] = last_row['positive_momentum']
            self.trades[type][time]['trade']['Momentums'] = last_row['momentum_ups']
            self.trades[type][time]['trade']['time'] = last_row['mom_t']
            self.trades[type][time]['trade']['ema'] = last_row['buy_ema']
            self.trades[type][time]['trade']['ema_value'] = last_row['mean_close_55']
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

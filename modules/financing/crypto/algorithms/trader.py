import pandas as pd
from bot.connect.message_connector import send_message, send_voice
from bot.connect.thread_connector import limit, async_fn
from modules.core.data.bot_system import system
from modules.financing.crypto.algorithms.extractor import get_binance_symbol_data, save_extracted_data, symbol_info, \
    get_file_name, get_type_trade, get_last_row_dataframe_by_time
from modules.financing.crypto.algorithms.processing import analysis, plot_df, supres, download_test_data, load_test_data
from time import sleep
import json
import numpy as np


class CryptoBot:

    def __init__(self, crypto, ref, exchange='BINANCE'):
        self.client = system('algorithms').client
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
        self.process_is_started = False
        self.first_iteration = False
        self.trade_type = 'micro'
        self.operative = False
        self.trade = {
            'temp': '',
            'operative': '',
            'value': 0,
            'last_temp': '',
            'last_time': '',
            'risk': 0
        }
        self.trades = {
            'large': {
                '1w': {
                    'trade': {
                        'high': 0,
                        'low': 0,
                        'close': 0,
                        'RSI': False,
                        'Momentum': False,
                        'ema': False
                    },
                    'trend': False,
                    'fingerprint': 0,
                    'buy': False,
                    'sell': False,
                    'buy_confirmation': False,
                    'sell_confirmation': False,
                    'support': [],
                    'resistance': [],
                },
                '1d': {
                    'trade': {
                        'high': 0,
                        'low': 0,
                        'close': 0,
                        'RSI': False,
                        'Momentum': False,
                        'ema': False
                    },
                    'trend': False,
                    'fingerprint': 0,
                    'buy': False,
                    'sell': False,
                    'buy_confirmation': False,
                    'sell_confirmation': False,
                    'support': [],
                    'resistance': [],
                },
            },
            'medium': {
                '4h': {
                    'trade': {
                        'high': 0,
                        'low': 0,
                        'close': 0,
                        'RSI': False,
                        'Momentum': False,
                        'ema': False
                    },
                    'trend': False,
                    'fingerprint': 0,
                    'buy': False,
                    'sell': False,
                    'buy_confirmation': False,
                    'sell_confirmation': False,
                    'support': [],
                    'resistance': [],
                },
                '1h': {
                    'trade': {
                        'high': 0,
                        'low': 0,
                        'close': 0,
                        'RSI': False,
                        'Momentum': False,
                        'ema': False
                    },
                    'trend': False,
                    'fingerprint': 0,
                    'buy': False,
                    'sell': False,
                    'buy_confirmation': False,
                    'sell_confirmation': False,
                    'support': [],
                    'resistance': [],
                },
            },
            'short': {
                '30m': {
                    'trade': {
                        'high': 0,
                        'low': 0,
                        'close': 0,
                        'RSI': False,
                        'Momentum': False,
                        'ema': False
                    },
                    'trend': False,
                    'fingerprint': 0,
                    'buy': False,
                    'sell': False,
                    'buy_confirmation': False,
                    'sell_confirmation': False,
                    'support': [],
                    'resistance': [],
                },
                '15m': {
                    'trade': {
                        'high': 0,
                        'low': 0,
                        'close': 0,
                        'RSI': False,
                        'Momentum': False,
                        'ema': False
                    },
                    'trend': False,
                    'fingerprint': 0,
                    'buy': False,
                    'sell': False,
                    'buy_confirmation': False,
                    'sell_confirmation': False,
                    'support': [],
                    'resistance': [],
                },
            },
            'micro': {
                '5m': {
                    'trade': {
                        'high': 0,
                        'low': 0,
                        'close': 0,
                        'RSI': False,
                        'Momentum': False,
                        'ema': False
                    },
                    'trend': False,
                    'fingerprint': 0,
                    'buy': False,
                    'sell': False,
                    'buy_confirmation': False,
                    'sell_confirmation': False,
                    'support': [],
                    'resistance': [],
                },
                '1m': {
                    'trade': {
                        'high': 0,
                        'low': 0,
                        'close': 0,
                        'RSI': False,
                        'Momentum': False,
                        'ema': False
                    },
                    'trend': False,
                    'fingerprint': 0,
                    'buy': False,
                    'sell': False,
                    'buy_confirmation': False,
                    'sell_confirmation': False,
                    'support': [],
                    'resistance': [],
                }
            }
        }
        self.configuration = {
            "1w": {
                'smas': [9, 55],
                'sma_s': 55,
                'sma_f': 9,
                'days': 1095,
                'days_s': 365,
                'days_t': 1095,
                'plot': 90
            },
            '1d': {
                'smas': [9, 55],
                'sma_s': 55,
                'sma_f': 9,
                'days': 270,
                'days_s': 45,
                'days_t': 90,
                'plot': 90
            },
            '4h': {
                'smas': [9, 55],
                'sma_s': 55,
                'sma_f': 9,
                'days': 60,
                'days_s': 15,
                'days_t': 60,
                'plot': 90
            },
            '1h': {
                'smas': [9, 55],
                'sma_s': 55,
                'sma_f': 9,
                'days': 30,
                'days_s': 15,
                'days_t': 60,
                'plot': 90
            },
            '30m': {
                'smas': [9, 55],
                'sma_s': 55,
                'sma_f': 9,
                'days': 3,
                'days_s': 1,
                'days_t': 30,
                'plot': 90
            },
            '15m': {
                'smas': [9, 55],
                'sma_s': 55,
                'sma_f': 9,
                'days': 3,
                'days_s': 1,
                'days_t': 30,
                'plot': 90
            },
            '5m': {
                'smas': [9, 55],
                'sma_s': 55,
                'sma_f': 9,
                'days': 3,
                'days_s': 1,
                'days_t': 30,
                'plot': 90
            },
            '1m': {
                'smas': [9, 55],
                'sma_s': 55,
                'sma_f': 9,
                'days': 3,
                'days_s': 1,
                'days_t': 15,
                'plot': 90
            },
        }
        self.updates = []
        self.testing = []

    @limit(1)
    @async_fn
    def start(self, cid=None):
        if not self.process_is_started:
            self.make_simulation(cid, download=True)
            send_message(cid, "Monitoreando %s " % self.symbol, play=True)
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

                        last_row = df.iloc[-1, :]
                        self.market_sentiment(last_row, time)
                        sleep(2)
                    self.first_iteration = True
                    self.take_decision(cid, False)
                    print(self.trades['micro']['1m']['fingerprint'], self.symbol)
                    sleep(30)
                except Exception as e:
                    print('Error: ', e)
        else:
            send_message(cid, "Monitoreando %s" % self.symbol, play=True)
            print('Ya se ha iniciado el monitoreo de %s' % self.symbol)

    def make_simulation(self, cid, download=False):
        try:

            if download:
                download_test_data(self.symbol, self.configuration.items())

            # Get Test Data
            load_test_data(self.configuration.items(), self.trades, self.symbol)

            main = self.trades[get_type_trade('1m', self.trades)]['1m']['data']
            main = main[
                main['timestamp'] > self.trades[get_type_trade('1d', self.trades)]['1d']['data'].loc[6, 'timestamp']]
            self.process_is_started = True
            self.first_iteration = True

            for index, row in main.iterrows():
                self.market_sentiment(row, '1m')
                self.market_sentiment(get_last_row_dataframe_by_time(self.trades, '5m', row['timestamp']), '5m')
                self.market_sentiment(get_last_row_dataframe_by_time(self.trades, '15m', row['timestamp']), '15m')
                self.market_sentiment(get_last_row_dataframe_by_time(self.trades, '30m', row['timestamp']), '30m')
                self.market_sentiment(get_last_row_dataframe_by_time(self.trades, '1h', row['timestamp']), '1h')
                self.market_sentiment(get_last_row_dataframe_by_time(self.trades, '4h', row['timestamp']), '4h')
                self.market_sentiment(get_last_row_dataframe_by_time(self.trades, '1d', row['timestamp']), '1d')
                self.market_sentiment(get_last_row_dataframe_by_time(self.trades, '1w', row['timestamp']), '1w')
                self.take_decision(cid=cid, play=False, testing=True)
                # print(self.trades['micro']['1m']['fingerprint'])

            df = pd.DataFrame(self.testing,
                              columns=['time', 'Action', 'Temp', 'Operative', 'Value', 'Profit', 'Result', 'Risk',
                                       'Time'])

            df.to_csv('backtesting/trades_%s.csv' % self.symbol, index=False)
            df = df[df['Result'] != 'Iniciado']
            df = df[df['Result'] != 'Actualización']
            df_new = df.groupby(['Operative', 'Result'])['Profit'].agg(['sum', 'count']).reset_index(drop=False)
            total = df_new['count'].sum()
            total_price = df_new['sum'].abs().sum()
            df_new['%_price'] = (df_new['count'] * 100) / total
            df_new['%_by_price'] = (df_new['sum'] * 100) / total_price
            df_new = df_new.round(2)
            df_new.to_csv('backtesting/result_%s.csv' % self.symbol, index=False)

        except Exception as e:
            print('Error: ', e)

    @limit(1)
    @async_fn
    def save_operative(self, temp, time, close, operative):
        self.trade['temp'] = temp
        self.trade['operative'] = operative
        self.trade['last_time'] = time
        self.trade['last_temp'] = temp
        self.trade['value'] = close
        self.trade['risk'] = 100

    @limit(1)
    @async_fn
    def save_update(self):
        update = {
            'temp': self.trade['temp'],
            'operative': self.trade['operative'],
            'last_time': self.trade['last_time'],
            'last_temp': self.trade['last_temp'],
            'value': self.trades['micro', '1m']['trade']['close'],
            'risk': self.trade['risk']
        }
        self.updates.append(update)

    @limit(1)
    @async_fn
    def show_operative(self, cid, play):
        if self.process_is_started:
            if self.operative:
                message = "%s\n" % self.symbol
                message += "%s - %s - Riesgo: %s \n" % (
                    self.trade['last_time'], ' 🟢 ' if self.trade['operative'] == 'long' else ' 🔴 ',
                    self.trade['risk'])
                message += "Inicial: %s - Actual: %s \n" % (
                    self.trade['value'], self.trades['micro']['1m']['trade']['close'])
                message += "Resultado: %s\n" % (self.profit())
            else:
                message = "No hay ninguna operativa para %s actualmente" % self.symbol
        else:
            message = "Primero se debe iniciar el proceso de monitoreo para %s" % self.symbol
        self.show_message(message=message, cid=cid, play=play)

    def show_results(self, cid, play, message, testing, temp, time, operative):
        self.operative = True
        self.save_operative(temp, time,
                            self.trades[temp][time]['trade']['close'],
                            operative)
        self.notify(testing=testing, message=message, action='Open', cid=cid, play=play)

    def validate_change_temp(self, testing):
        change = False

        if self.trade['operative'] == 'long':
            if self.trade['last_time'] == '1m':
                if self.trades['micro']['5m']['trade']['ema']:
                    self.trade['risk'] = self.trade['risk'] - 10
                    self.trade['last_time'] = '5m'
                    change = True
            if self.trade['last_time'] == '5m':
                if self.trades['short']['15m']['trade']['ema']:
                    self.trade['risk'] = self.trade['risk'] - 10
                    self.trade['last_time'] = '15m'
                    self.trade['last_temp'] = 'short'
                    change = True
            if self.trade['last_time'] == '15m':
                if self.trades['short']['30m']['trade']['ema']:
                    self.trade['risk'] = self.trade['risk'] - 10
                    self.trade['last_time'] = '30m'
                    self.trade['last_temp'] = 'short'
                    change = True
            if self.trade['last_time'] == '30m':
                if self.trades['medium']['1h']['trade']['ema']:
                    self.trade['risk'] = self.trade['risk'] - 10
                    self.trade['last_time'] = '1h'
                    self.trade['last_temp'] = 'medium'
                    change = True
            if self.trade['last_time'] == '1h':
                if self.trades['medium']['4h']['trade']['ema']:
                    self.trade['risk'] = self.trade['risk'] - 10
                    self.trade['last_time'] = '4h'
                    self.trade['last_temp'] = 'medium'
                    change = True

        if self.trade['operative'] == 'short':
            if self.trade['last_time'] == '1m':
                if not self.trades['micro']['5m']['trade']['ema']:
                    self.trade['risk'] = self.trade['risk'] - 10
                    self.trade['last_time'] = '5m'
                    change = True
            if self.trade['last_time'] == '5m':
                if not self.trades['short']['15m']['trade']['ema']:
                    self.trade['risk'] = self.trade['risk'] - 10
                    self.trade['last_time'] = '15m'
                    self.trade['last_temp'] = 'short'
                    change = True
            if self.trade['last_time'] == '15m':
                if not self.trades['short']['30m']['trade']['ema']:
                    self.trade['risk'] = self.trade['risk'] - 10
                    self.trade['last_time'] = '30m'
                    self.trade['last_temp'] = 'short'
                    change = True
            if self.trade['last_time'] == '30m':
                if not self.trades['medium']['1h']['trade']['ema']:
                    self.trade['risk'] = self.trade['risk'] - 10
                    self.trade['last_time'] = '1h'
                    self.trade['last_temp'] = 'medium'
                    change = True
            if self.trade['last_time'] == '1h':
                if not self.trades['medium']['4h']['trade']['ema']:
                    self.trade['risk'] = self.trade['risk'] - 10
                    self.trade['last_time'] = '4h'
                    self.trade['last_temp'] = 'medium'
                    change = True

        if change:
            self.notify(testing=testing, message='Actualización', action='Update')

        return False

    def profit(self):
        if self.trade['operative'] == 'long':
            diff = float(self.trades['micro']['1m']['trade']['close']) - (
                float(self.trade['value']))
        else:
            diff = (float(self.trade['value'])) - float(
                self.trades['micro']['1m']['trade']['close'])
        return round(diff, 2)

    def notify(self, testing, message, action, cid=None, play=False):
        if not testing:
            self.show_message(message="%s de %s %s en %s" % (
                self.trade['operative'], self.symbol, message, self.trades['micro']['1m']['trade']['close']), cid=cid,
                              play=play)
            if action == 'Open':
                message = "%s ALERTA de %s en %s" % (
                    self.crypto, ('COMPRA' if self.trade['operative'] == 'long' else 'VENTA'),
                    self.trades['micro']['1m']['trade']['close'])
            if action == 'Update':
                message = "%s ALERTA de actualización en %s" % (
                    self.crypto, self.trades['micro']['1m']['trade']['close'])
            if action == 'Close':
                message = "%s ALERTA de cerrar en %s" % (self.crypto, self.trades['micro']['1m']['trade']['close'])
            send_voice(message)
            send_voice(message)
            send_voice(message)
        else:
            win = ''
            if action != 'Close':
                diff = 0
                win = message
            else:
                diff = self.profit()
                win = 'Ganado' if diff > 0 else 'Perdido'

            row = [self.trades['micro']['1m']['fingerprint'], action,
                   self.trade['temp'], self.trade['operative'],
                   self.trades['micro']['1m']['trade']['close'], diff, win,
                   self.trade['risk'],
                   self.trade['last_time']]
            self.testing.append(row)

    def evaluate_operative(self, testing, cid, play):
        temp = None
        close = False
        close = self.validate_change_temp(testing)

        # Long
        if self.trade['operative'] == 'long':
            if self.trade['last_time'] == '1m':
                if not self.trades['micro']['1m']['trade']['mean_f'] and (
                        not self.trades['short']['15m']['trade']['Momentum']):
                    temp = 'Long'
                    close = True
            if self.trade['last_time'] == '5m':
                if not self.trades['micro']['5m']['trade']['mean_f'] and (
                        not self.trades['short']['30m']['trade']['Momentum']):
                    temp = 'Long'
                    close = True
            if self.trade['last_time'] == '15m':
                if (not self.trades['short']['15m']['trade']['mean_f'] and (
                        not self.trades['short']['30m']['trade']['Momentum']) and (
                        not self.trades['micro']['5m']['trade']['Momentum'])):
                    temp = 'Long'
                    close = True
            if self.trade['last_time'] == '30m':
                if (not self.trades['short']['30m']['trade']['mean_f'] and (
                        not self.trades['medium']['1h']['trade']['Momentum']) and (
                            not self.trades['short']['15m']['trade']['Momentum'])) or (  # Brake all if temp is negative
                        not self.trades['micro']['1m']['trade']['Momentum'] and
                        not self.trades['micro']['5m']['trade']['Momentum'] and
                        not self.trades['short']['15m']['trade']['Momentum'] and
                        not self.trades['short']['30m']['trade']['Momentum']
                ):
                    temp = 'Long'
                    close = True
            if self.trade['last_time'] == '1h':
                if (not self.trades['medium']['1h']['trade']['mean_f'] and (
                        not self.trades['medium']['4h']['trade']['Momentum']) and (
                            not self.trades['short']['30m']['trade']['Momentum']) and (
                            not self.trades['short']['15m']['trade']['Momentum'])):
                    temp = 'Long'
                    close = True
            if self.trade['last_time'] == '4h':
                if (not self.trades['medium']['4h']['trade']['mean_f'] and (
                        (not self.trades['large']['1d']['trade']['Momentum']) or (
                        not self.trades['medium']['1h']['trade']['Momentum']))):
                    temp = 'Long'
                    close = True
        # Short
        else:
            if self.trade['last_time'] == '1m':
                if self.trades['micro']['1m']['trade']['mean_f'] and (
                        self.trades['short']['15m']['trade']['Momentum']):
                    temp = 'Short'
                    close = True
            if self.trade['last_time'] == '5m':
                if not self.trades['micro']['5m']['trade']['mean_f'] and (
                        self.trades['short']['30m']['trade']['Momentum']):
                    temp = 'Short'
                    close = True
            if self.trade['last_time'] == '15m':
                if not self.trades['short']['15m']['trade']['mean_f'] and (
                        self.trades['short']['30m']['trade']['Momentum']) and (
                        self.trades['micro']['5m']['trade']['Momentum']) or (
                        self.trades['micro']['5m']['trade']['ema']):
                    temp = 'Short'
                    close = True
            if self.trade['last_time'] == '30m':
                if (not self.trades['short']['30m']['trade']['mean_f'] and (
                        self.trades['medium']['1h']['trade']['Momentum']) and (
                            self.trades['short']['15m']['trade']['Momentum'])) or (
                        self.trades['short']['15m']['trade']['ema']):
                    temp = 'Short'
                    close = True
            if self.trade['last_time'] == '1h':
                if (not self.trades['medium']['1h']['trade']['mean_f'] and (
                        self.trades['medium']['4h']['trade']['mean_f']) and (
                            self.trades['short']['30m']['trade']['Momentum']) and (
                            self.trades['short']['15m']['trade']['Momentum'])) or (
                        self.trades['short']['30m']['trade']['ema']):
                    temp = 'Short'
                    close = True
            if self.trade['last_time'] == '4h':
                if (not self.trades['medium']['4h']['trade']['mean_f'] and ((
                                                                                    self.trades['large']['1d']['trade'][
                                                                                        'Momentum']) or (
                                                                                    self.trades['medium']['1h'][
                                                                                        'trade']['Momentum']))) or (
                        self.trades['medium']['1h']['trade']['ema']):
                    temp = 'Short'
                    close = True
        if close:
            self.operative = False
            if not testing:
                self.show_message(
                    message='Cerrar %s de %s en %s' % (temp, self.symbol, self.trades['micro']['1m']['trade']['close']),
                    cid=cid, play=play)
            else:
                self.notify(testing=testing, message='Cierre', action='Close')

    def take_decision(self, cid=None, play=False, testing=False):
        # Micro Trade
        if not self.operative:
            if self.trade_type == 'micro':
                # Long
                if ((self.trades['micro']['1m']['trade']['mean_f'] and
                     self.trades['micro']['1m']['trade']['Momentum']) and (
                            self.trades['micro']['1m']['trade']['confirm_dir'] and
                            self.trades['micro']['1m']['trade']['confirm_dir_ups'] > 1)) and not (
                        not self.trades['micro']['1m']['trade']['Momentum'] and
                        not self.trades['micro']['5m']['trade']['Momentum'] and
                        not self.trades['short']['15m']['trade']['Momentum']):
                    self.show_results(cid, play, 'Iniciado', testing, 'micro', '1m', 'long')
                # Short
                if ((not self.trades['micro']['1m']['trade']['mean_f']) and (
                        not self.trades['micro']['1m']['trade']['Momentum']) and (
                            not self.trades['micro']['1m']['trade']['confirm_dir'] and
                            self.trades['micro']['1m']['trade']['confirm_dir_ups'] > 1)) and not (
                        self.trades['micro']['1m']['trade']['Momentum'] and
                        self.trades['micro']['5m']['trade']['Momentum'] and
                        self.trades['short']['15m']['trade']['Momentum']):
                    self.show_results(cid, play, 'Iniciado', testing, 'micro', '1m', 'short')
        else:
            self.evaluate_operative(testing, cid, play)

    def market_sentiment(self, last_row, time):
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

        trade = self.save_trade(time, last_row, trade)

        return trade

    def save_trade(self, time, last_row, trade):
        # Fingerprint
        fingerprint = last_row['time']

        type = get_type_trade(time, self.trades)

        if self.trades[type][time]['fingerprint'] == fingerprint and trade:
            return False
        else:
            self.trades[type][time]['fingerprint'] = last_row['time']
            self.trades[type][time]['trend'] = last_row['trend']
            self.trades[type][time]['buy'] = last_row['buy_trend']
            self.trades[type][time]['sell'] = last_row['sell_trend']
            self.trades[type][time]['buy_confirmation'] = last_row['buy_confirmation']
            self.trades[type][time]['sell_confirmation'] = last_row['sell_confirmation']
            self.trades[type][time]['trade']['high'] = last_row['high']
            self.trades[type][time]['trade']['low'] = last_row['low']
            self.trades[type][time]['trade']['close'] = last_row['close']
            self.trades[type][time]['trade']['RSI'] = last_row['positive_RSI']
            self.trades[type][time]['trade']['RSI_value'] = last_row['RSI']
            self.trades[type][time]['trade']['last_RSI_value'] = last_row['RSI_rv']
            self.trades[type][time]['trade']['RSIs'] = last_row['RSI_ups']
            self.trades[type][time]['trade']['mean_f'] = last_row['mean_f_diff_res']
            self.trades[type][time]['trade']['mean_f_ups'] = last_row['ema_f_ups']
            self.trades[type][time]['trade']['Momentum'] = last_row['positive_momentum']
            self.trades[type][time]['trade']['Momentums'] = last_row['momentum_ups']
            self.trades[type][time]['trade']['confirm_dir'] = last_row['DIFF']
            self.trades[type][time]['trade']['confirm_dir_ups'] = last_row['ups']
            self.trades[type][time]['trade']['variation'] = last_row['close_variation']
            self.trades[type][time]['trade']['time'] = last_row['mom_t']
            self.trades[type][time]['trade']['ema'] = last_row['buy_ema']
            self.trades[type][time]['trade']['ema_value'] = last_row['mean_close_55']
            return True

    def get_market_graphs(self, bot=None, cid=None):

        for time, options in self.configuration.items():
            try:
                # Get Data
                data = get_binance_symbol_data(symbol=self.symbol, kline_size=time, auto_increment=False,
                                               save=True, sma=options['days'])
                # Analyse
                options['data'] = analysis(df=data, ma_f=options['sma_f'], ma_s=options['sma_s'],
                                           mas=options['smas'], time=time)
                save_extracted_data(symbol=self.symbol, df=options['data'], form='sma-%s' % options['days'],
                                    size=time)
                # options['min_max'] = get_stats(df=self.data)
                df = options['data'].tail(120)
                if len(df.index) > options['plot']:
                    options['support'], options['resistance'] = supres(df['close'].to_numpy(), options['plot'])
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

    def update_symbol_info(self):
        self.symbol_info = symbol_info(crypto=self.crypto, ref=self.ref, exchange=self.exchange)


class CustomJSONizer(json.JSONEncoder):
    def default(self, obj):
        return super().encode(bool(obj)) \
            if isinstance(obj, np.bool_) \
            else super().default(obj)

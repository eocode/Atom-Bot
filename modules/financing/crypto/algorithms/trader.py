import pandas as pd

from bot.connect.message_connector import send_message, send_voice
from bot.connect.thread_connector import limit, async_fn
from modules.core.data.bot_system import system
from modules.financing.crypto.algorithms.extractor import get_binance_symbol_data, save_extracted_data, \
    get_file_name, get_type_trade, get_last_row_dataframe_by_time
from modules.financing.crypto.algorithms.processing import analysis, plot_df, supres, download_test_data, load_test_data
from time import sleep
from datetime import datetime


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
                'days_s': 2000,
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
        self.testing = []
        self.cids = []

    def send_messages(self, message, play=False, alert=False):
        print('ALERT')
        print(message)
        for cid in self.cids:
            send_message(cid=cid, text=message, play=play)
        if alert:
            send_voice("Alerta")
            send_voice("Alerta")

    @limit(1)
    @async_fn
    def start(self, cid=None):
        if not self.process_is_started:
            self.cids.append(cid)
            self.make_simulation(download=True)
            self.send_messages(message="Monitoreando %s " % self.crypto)
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
                        self.save_trade(last_row=last_row, time=time)
                        sleep(2)
                    self.first_iteration = True
                    self.take_decision(testing=False)
                    print(self.trades['micro']['1m']['fingerprint'], self.symbol)
                    sleep(30)
                except Exception as e:
                    print('Error: ', e)
        else:
            self.send_messages(message="Monitoreando %s " % self.crypto)
            print('Ya se ha iniciado el monitoreo de %s' % self.symbol)

    def make_simulation(self, download=False):
        try:

            if download:
                download_test_data(self.symbol, self.configuration.items())

            # Get Test Data
            load_test_data(self.configuration.items(), self.trades, self.symbol)

            main = self.trades[get_type_trade('1m', self.trades)]['1m']['data']

            open = pd.read_csv('backtesting/trades_%s.csv' % self.symbol)
            timestamp = open[open['Action'] == 'Open'].reset_index().loc[3, 'time']

            print("Initial Analysis: ", timestamp, self.crypto)

            main = main[main['timestamp'] >= timestamp]
            self.process_is_started = True
            self.first_iteration = True

            for index, row in main.iterrows():
                self.save_trade(last_row=row, time='1m')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '5m', row['timestamp']), time='5m')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '15m', row['timestamp']),
                                time='15m')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '30m', row['timestamp']),
                                time='30m')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '1h', row['timestamp']), time='1h')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '4h', row['timestamp']), time='4h')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '1d', row['timestamp']), time='1d')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '1w', row['timestamp']), time='1w')
                self.take_decision(testing=True)

            df = pd.DataFrame(self.testing,
                              columns=['time', 'Action', 'Temp', 'Operative', 'Value', 'Profit', 'Result', 'Risk',
                                       'Time', 'Elapsed', 'Min', 'Max'])

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

            gain = df_new[df_new['Result'] == 'Ganado']
            trades = gain['%_price'].sum()
            variation = gain['sum'].sum()
            prices = gain['%_by_price'].sum()
            message = "Eficiencia %s: \n\n%s Ganados: \ntrades: %s margen: %s \n" % (
                self.crypto, round(variation, 2), int(round(trades, 0)), int(round(prices, 0)))
            loss = df_new[df_new['Result'] == 'Perdido']
            variation = loss['sum'].sum()
            trades = loss['%_price'].sum()
            prices = loss['%_by_price'].sum()
            message += "%s Perdidos: \ntrades: %s margen: %s" % (
                round(variation, 2), int(round(trades, 0)), int(round(prices, 0)))
            self.send_messages(message=message)

        except Exception as e:
            print('Error: ', e)

    def elapsed_time(self, current=True):
        if current:
            diff = (datetime.utcnow() - self.trade['fingerprint'])
        else:
            date_time_obj = datetime.strptime(str(self.trades['micro']['1m']['fingerprint']), '%Y-%m-%d %H:%M:%S')
            diff = (date_time_obj - self.trade['fingerprint'])
        return round(diff.total_seconds() / 60 / 60, 2)

    def trade_variation(self, current):
        return round((1 - (current / self.trade['value'])) * 100, 2)

    def save_operative(self, temp, time, close, operative):
        self.trade['temp'] = temp
        self.trade['operative'] = operative
        self.trade['last_time'] = time
        self.trade['last_temp'] = temp
        self.trade['value'] = close
        self.trade['risk'] = 100
        date_time_obj = datetime.strptime(str(self.trades['micro']['1m']['fingerprint']), '%Y-%m-%d %H:%M:%S')
        self.trade['fingerprint'] = date_time_obj
        self.trade['max'] = close
        self.trade['min'] = close

    @limit(1)
    @async_fn
    def show_operative(self):
        if self.process_is_started:
            if self.operative:
                message = "%s\n" % self.symbol
                message += "%s - %s - Riesgo: %s \n" % (
                    self.trade['last_time'], ' 🟢 ' if self.trade['operative'] == 'long' else ' 🔴 ',
                    self.trade['risk'])
                message += "Inicial: %s - Actual: %s \n" % (
                    self.trade['value'], self.trades['micro']['1m']['trade']['close'])
                message += "Resultado: %s con %s\n\nStats\n" % (
                    self.profit(), self.trade_variation(self.trades['micro']['1m']['trade']['close']))

                message += "Tiempo: %s hrs\n" % (self.elapsed_time(current=True))
                message += "Máximo: %s con %s\n" % (
                    round(self.trade['max']), self.trade_variation(round(self.trade['max'])))
                message += "Minimo: %s con %s" % (
                    round(self.trade['min']), self.trade_variation(round(self.trade['min'])))
            else:
                message = "No hay ninguna operativa para %s actualmente" % self.symbol
        else:
            message = "Primero se debe iniciar el proceso de monitoreo para %s" % self.symbol
        self.send_messages(message=message)

    def show_results(self, message, testing, temp, time, operative):
        self.operative = True
        self.save_operative(temp, time,
                            self.trades[temp][time]['trade']['close'],
                            operative)
        self.notify(testing=testing, message=message, action='Open')

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

    def notify(self, testing, message, action):
        if action == 'Open':
            diff = 0
            win = message
        else:
            diff = self.profit()
            win = 'Ganado' if diff >= 0 else 'Perdido'

        if not testing:
            if action == 'Open':
                message = "Inicia %s %s en %s" % (
                    ('COMPRA' if self.trade['operative'] == 'long' else 'VENTA'), self.crypto,
                    round(self.trades['micro']['1m']['trade']['close'], 0))
            if action == 'Update':
                message = "Continua %s en %s" % (
                    self.crypto, round(self.trades['micro']['1m']['trade']['close'], 0))
            if action == 'Close':
                message = "Cierra %s en %s\n" % (self.crypto, self.trades['micro']['1m']['trade']['close'])
                message += "Resultado: %s" % win
            self.send_messages(message=message, play=False, alert=True)
            self.send_messages(message=message, play=False, alert=True)
        else:
            row = [self.trades['micro']['1m']['fingerprint'], action,
                   self.trade['temp'], self.trade['operative'],
                   self.trades['micro']['1m']['trade']['close'], diff, win,
                   self.trade['risk'],
                   self.trade['last_time'], self.elapsed_time(current=False), self.trade['min'], self.trade['max']]
            self.testing.append(row)

    def evaluate_operative(self, testing):

        close = self.validate_change_temp(testing)

        # Long
        if self.trade['operative'] == 'long':
            if self.trade['last_time'] == '1m':
                if not self.trades['micro']['1m']['trade']['mean_f'] and (
                        not self.trades['short']['15m']['trade']['Momentum']) or (
                        not self.trades['micro']['1m']['trade']['Momentum'] and
                        not self.trades['short']['15m']['trade']['Momentum'] and
                        not self.trades['short']['30m']['trade']['Momentum']
                ):
                    close = True
            if self.trade['last_time'] == '5m':
                if not self.trades['micro']['5m']['trade']['mean_f'] and (
                        not self.trades['short']['30m']['trade']['Momentum']):
                    close = True
            if self.trade['last_time'] == '15m':
                if (not self.trades['short']['15m']['trade']['mean_f'] and (
                        not self.trades['short']['30m']['trade']['Momentum']) and (
                        not self.trades['micro']['5m']['trade']['Momentum'])):
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
                    close = True
            if self.trade['last_time'] == '1h':
                if (not self.trades['medium']['1h']['trade']['mean_f'] and (
                        not self.trades['medium']['4h']['trade']['Momentum']) and (
                        not self.trades['short']['30m']['trade']['Momentum']) and (
                        not self.trades['short']['15m']['trade']['Momentum'])):
                    close = True
            if self.trade['last_time'] == '4h':
                if (not self.trades['medium']['4h']['trade']['mean_f'] and (
                        (not self.trades['large']['1d']['trade']['Momentum']) or (
                        not self.trades['medium']['1h']['trade']['Momentum']))):
                    close = True
        # Short
        else:
            if self.trade['last_time'] == '1m':
                if self.trades['micro']['1m']['trade']['mean_f'] and (
                        self.trades['short']['15m']['trade']['Momentum']) or (
                        self.trades['micro']['1m']['trade']['Momentum'] and
                        self.trades['short']['15m']['trade']['Momentum'] and
                        self.trades['short']['30m']['trade']['Momentum'] and (

                        )
                ):
                    close = True
            if self.trade['last_time'] == '5m':
                if self.trades['micro']['5m']['trade']['mean_f'] and (
                        self.trades['short']['30m']['trade']['Momentum']) or (
                        self.trades['micro']['1m']['trade']['RSI_value'] <= 17 and
                        self.trades['micro']['5m']['trade']['RSI_value'] <= 20 and
                        not self.trades['micro']['5m']['trade']['Momentum'] and
                        not self.trades['micro']['1m']['trade']['Momentum'] and
                        abs(self.trades['micro']['1m']['trade']['Momentum_value']) > 19
                ):
                    close = True
            if self.trade['last_time'] == '15m':
                if self.trades['short']['15m']['trade']['mean_f'] and (
                        self.trades['short']['15m']['trade']['Momentum'] and
                        self.trades['micro']['5m']['trade']['Momentum'] and
                        self.trades['micro']['1m']['trade']['Momentum']) or (
                        self.trades['micro']['5m']['trade']['ema']):
                    close = True
            if self.trade['last_time'] == '30m':
                if (self.trades['short']['30m']['trade']['mean_f'] and (
                        self.trades['medium']['1h']['trade']['Momentum']) and (
                            self.trades['short']['15m']['trade']['Momentum'])) or (  # Brake all if temp is negative
                        self.trades['micro']['1m']['trade']['Momentum'] and
                        self.trades['micro']['5m']['trade']['Momentum'] and
                        self.trades['short']['15m']['trade']['Momentum'] and
                        self.trades['short']['30m']['trade']['Momentum']):
                    close = True
            if self.trade['last_time'] == '1h':
                if (self.trades['medium']['1h']['trade']['mean_f'] and (
                        self.trades['medium']['4h']['trade']['mean_f']) and (
                            self.trades['short']['30m']['trade']['Momentum']) and (
                            self.trades['short']['15m']['trade']['Momentum'])) or (
                        self.trades['short']['30m']['trade']['ema']):
                    close = True
            if self.trade['last_time'] == '4h':
                if (self.trades['medium']['4h']['trade']['mean_f'] and (
                        (self.trades['large']['1d']['trade']['Momentum']) or (
                        self.trades['medium']['1h']['trade']['Momentum']))) or (
                        self.trades['medium']['1h']['trade']['ema']):
                    close = True
        if close:
            self.operative = False
            self.notify(testing=testing, message='Cierre', action='Close')

    def take_decision(self, testing=False):
        # Micro Trade
        if not self.operative:
            if self.trade_type == 'micro':
                # Long
                if ((self.trades['micro']['1m']['trade']['mean_f'] and
                     self.trades['micro']['1m']['trade']['Momentum']) and (
                            self.trades['micro']['1m']['trade']['confirm_dir'] and
                            self.trades['short']['15m']['trade']['RSI'] and
                            self.trades['micro']['1m']['trade']['confirm_dir_ups'] > 1)) and not (
                        not self.trades['micro']['1m']['trade']['Momentum'] and
                        not self.trades['micro']['5m']['trade']['Momentum'] and
                        not self.trades['short']['15m']['trade']['Momentum']) and (
                        self.trades['micro']['1m']['trade']['RSI_value'] < 70
                ):
                    self.show_results('Iniciado', testing, 'micro', '1m', 'long')
                # Short
                if ((not self.trades['micro']['1m']['trade']['mean_f'] and
                     not self.trades['micro']['1m']['trade']['Momentum']) and (
                            not self.trades['micro']['1m']['trade']['Momentum'] and
                            not self.trades['micro']['5m']['trade']['Momentum']) and (
                            not self.trades['micro']['1m']['trade']['confirm_dir'] and
                            not self.trades['short']['15m']['trade']['RSI'] and
                            not self.trades['micro']['1m']['trade']['RSI'] and
                            self.trades['micro']['1m']['trade']['confirm_dir_ups'] > 1)) and not (
                        self.trades['micro']['1m']['trade']['Momentum'] and
                        self.trades['micro']['5m']['trade']['Momentum'] and
                        self.trades['short']['15m']['trade']['Momentum']
                ):
                    self.show_results('Iniciado', testing, 'micro', '1m', 'short')
        else:
            self.trade['max'] = self.trades['micro']['1m']['trade']['close'] if self.trades['micro']['1m']['trade'][
                                                                                    'close'] > self.trade['max'] else \
                self.trade['max']
            self.trade['min'] = self.trades['micro']['1m']['trade']['close'] if self.trades['micro']['1m']['trade'][
                                                                                    'close'] < self.trade['min'] else \
                self.trade['min']
            self.evaluate_operative(testing)

    def save_trade(self, time, last_row):
        # Fingerprint
        fingerprint = last_row['time']

        type = get_type_trade(time, self.trades)

        if self.trades[type][time]['fingerprint'] == fingerprint:
            return False
        else:
            self.trades[type][time]['fingerprint'] = last_row['time']
            self.trades[type][time]['trend'] = last_row['trend']
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
            self.trades[type][time]['trade']['Momentum_value'] = last_row['momentum']
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
                        send_message(cid=cid, text=time, play=False)
                        bot.send_photo(cid, photo)
            except Exception as e:
                print('Error PLOT: ', e)

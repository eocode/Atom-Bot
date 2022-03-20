import time

import pandas as pd

from bot.connect.message_connector import send_message, send_voice
from bot.connect.thread_connector import limit, async_fn
from modules.core.data.bot_system import system
from modules.financing.crypto.algorithms.configuration import configuration
from modules.financing.crypto.algorithms.extractor import get_binance_symbol_data, save_extracted_data, \
    get_file_name, get_type_trade, get_last_row_dataframe_by_time
from modules.financing.crypto.algorithms.processing import analysis, plot_df, supres, download_test_data, load_test_data
from time import sleep
import datetime

from modules.financing.crypto.algorithms.trades import trades


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
        self.indicators = ['timestamp', 'fast', 'fast_ups', 'avg',
                           'price_up', 'price_ups', 'momentums', 'momentum',
                           'momentum_ups', 'buy_ema', 'RSI', 'RSIs', 'RSI_ups',
                           'close', 'open', 'close_variation']
        self.trade = {
            'temp': '',
            'operative': '',
            'value': 0,
            'last_temp': '',
            'last_time': '',
            'risk': 0,
            'action': ''
        }
        self.trades = trades[self.crypto]
        self.testing = []
        self.cids = []

    def send_messages(self, message, play=False, alert=False, runs=1):
        print('ALERT')
        print(message)
        for i in range(runs):
            for cid in self.cids:
                send_message(cid=cid, text=message, play=play)
                time.sleep(runs)
            if alert:
                send_voice(self.trade['action'])

    @limit(1)
    @async_fn
    def start(self, cid=None):
        if not self.process_is_started:
            self.cids.append(cid)
            self.make_simulation(download=True)
            self.send_messages(message="Monitoreando %s " % self.crypto)
            self.process_is_started = True
            while True:
                # For all temps
                try:
                    current_minute = datetime.datetime.now().minute
                    if current_minute != self.trades['micro']['1m']['last_minute']:
                        for size, options in configuration.items():
                            # Get Data
                            data = get_binance_symbol_data(symbol=self.symbol, kline_size=size, auto_increment=False,
                                                           save=False, sma=options['days_s'])
                            # Analyse
                            options['data'] = analysis(df=data, ma_f=options['sma_f'], ma_s=options['sma_s'])
                            df = options['data'].tail(365)

                            last_row = df.iloc[-1, :]
                            self.save_trade(last_row=last_row, size=size)
                            sleep(2)
                        self.first_iteration = True
                        self.take_decision(testing=False)
                        print(self.trades['micro']['1m']['fingerprint'], self.symbol)
                except Exception as e:
                    print('Error: ', e)
        else:
            self.send_messages(message="Monitoreando %s " % self.crypto)
            print('Ya se ha iniciado el monitoreo de %s' % self.symbol)

    def make_simulation(self, download=False):
        try:

            if download:
                download_test_data(self.symbol, configuration.items(), self.indicators)

            # Get Test Data
            load_test_data(configuration.items(), self.trades, self.symbol)

            main = self.trades[get_type_trade('1m', self.trades)]['1m']['data']

            tod = datetime.datetime.now()
            d = datetime.timedelta(days=15)
            timestamp = tod - d

            print("Initial Analysis: ", timestamp, self.crypto)

            main = main[main['timestamp'] >= str(timestamp)]
            self.process_is_started = True
            self.first_iteration = True

            for index, row in main.iterrows():
                self.save_trade(last_row=row, size='1m')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '5m', row['timestamp']), size='5m')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '15m', row['timestamp']),
                                size='15m')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '30m', row['timestamp']),
                                size='30m')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '1h', row['timestamp']), size='1h')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '4h', row['timestamp']), size='4h')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '1d', row['timestamp']), size='1d')
                self.save_trade(last_row=get_last_row_dataframe_by_time(self.trades, '1w', row['timestamp']), size='1w')
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
            gains = gain['%_price'].sum()
            variation = gain['sum'].sum()
            prices = gain['%_by_price'].sum()
            message = "Eficiencia %s: \n\n%s Ganados: \ntrades: %s margen: %s \n" % (
                self.crypto, round(variation, 2), int(round(gains, 0)), int(round(prices, 0)))
            loss = df_new[df_new['Result'] == 'Perdido']
            variation = loss['sum'].sum()
            losses = loss['%_price'].sum()
            prices = loss['%_by_price'].sum()
            message += "%s Perdidos: \ntrades: %s margen: %s" % (
                round(variation, 2), int(round(losses, 0)), int(round(prices, 0)))
            self.send_messages(message=message)

        except Exception as e:
            print('Error: ', e)

    def elapsed_time(self, current=True):
        return round(self.elapsed_minutes(current=current) / 60, 2)

    def elapsed_minutes(self, current=True):
        if current:
            diff = (datetime.datetime.utcnow() - self.trade['fingerprint'])
        else:
            date_time_obj = datetime.datetime.strptime(str(self.trades['micro']['1m']['fingerprint']),
                                                       '%Y-%m-%d %H:%M:%S')
            diff = (date_time_obj - self.trade['fingerprint'])
        return round(diff.total_seconds() / 60, 2)

    def trade_variation(self, current):
        return abs(round((1 - (current / self.trade['value'])) * 100, 2))

    def save_operative(self, temp, size, close, operative):
        self.trade['temp'] = temp
        self.trade['operative'] = operative
        self.trade['last_time'] = size
        self.trade['last_temp'] = temp
        self.trade['value'] = close
        self.trade['risk'] = 100
        date_time_obj = datetime.datetime.strptime(str(self.trades['micro']['1m']['fingerprint']), '%Y-%m-%d %H:%M:%S')
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
                message += "Minimo: %s con %s\n\n" % (
                    round(self.trade['min']), self.trade_variation(round(self.trade['min'])))
                message += "%s de %s hrs con %s periodos" % (
                    ('Long' if self.trades['short']['30m']['trade']['Momentum'] else 'Short'),
                    ((self.trades['short']['30m']['trade']['Momentums']) * 30) / 60,
                    self.trades['short']['30m']['trade']['Momentums'])
            else:
                message = "No hay ninguna operativa para %s actualmente" % self.symbol
        else:
            message = "Primero se debe iniciar el proceso de monitoreo para %s" % self.symbol
        self.send_messages(message=message)

    def show_results(self, message, testing, temp, size, operative):
        self.operative = True
        self.save_operative(temp, size,
                            self.trades[temp][size]['trade']['close'],
                            operative)
        self.notify(testing=testing, message=message, action='Abrir')

    def profit(self):
        if self.trade['operative'] == 'long':
            diff = float(self.trades['micro']['1m']['trade']['close']) - (
                float(self.trade['value']))
        else:
            diff = (float(self.trade['value'])) - float(
                self.trades['micro']['1m']['trade']['close'])
        return round(diff, 2)

    def notify(self, testing, message, action):
        if action == 'Abrir':
            diff = 0
            win = message
        else:
            diff = self.profit()
            win = 'Ganado' if diff >= 0 else 'Perdido'

        if not testing:
            self.trade['action'] = action
            if action == 'Abrir':
                message = "Inicia %s %s en %s" % (
                    ('COMPRA' if self.trade['operative'] == 'long' else 'VENTA'), self.crypto,
                    round(self.trades['micro']['1m']['trade']['close'], 0))
            if action == 'Continua':
                message = "Continua %s %s en %s" % (
                    self.crypto, self.trade['operative'], round(self.trades['micro']['1m']['trade']['close'], 0))
            if action == 'Cerrar':
                message = "Cierra %s en %s\n" % (self.crypto, self.trades['micro']['1m']['trade']['close'])
                message += "Resultado: %s con %s" % (win, self.profit())
            self.send_messages(message=message, play=False, alert=True, runs=3)
        else:
            row = [self.trades['micro']['1m']['fingerprint'], action,
                   self.trade['temp'], self.trade['operative'],
                   self.trades['micro']['1m']['trade']['close'], diff, win,
                   self.trade['risk'],
                   self.trade['last_time'], self.elapsed_time(current=False), self.trade['min'], self.trade['max']]
            self.testing.append(row)

    def evaluate_operative(self, testing):

        close = False

        # Long
        if self.trade['operative'] == 'long':
            if (not self.trades['short']['15m']['trade']['RSI'] and
                not self.trades['micro']['5m']['trade']['RSI'] and
                not self.trades['micro']['5m']['trade']['mean_f']) or (
                    not self.trades['short']['30m']['trade']['Momentum']):
                close = True

        # Short
        else:
            if ((self.trades['short']['15m']['trade']['RSI'] and
                 self.trades['micro']['5m']['trade']['RSI'] and
                 self.trades['micro']['5m']['trade']['Momentum'] and
                 self.trades['micro']['5m']['trade']['mean_f']) or (
                    self.trades['short']['30m']['trade']['Momentum'])):
                close = True

        if close:
            self.operative = False
            self.notify(testing=testing, message='Cierre', action='Cerrar')

    def take_decision(self, testing=False):
        # Micro Trade
        if not self.operative:
            if self.trade_type == 'micro':
                # Long
                if (self.trades['micro']['5m']['trade']['RSI'] and
                    self.trades['micro']['1m']['trade']['RSI'] and
                    self.trades['short']['15m']['trade']['RSI'] and
                    self.trades['short']['30m']['trade']['RSI'] and
                    self.trades['medium']['1h']['trade']['RSI'] and
                    self.trades['medium']['4h']['trade']['RSI']) and (
                        self.trades['short']['30m']['trade']['Momentum']):
                    self.show_results('Iniciado', testing, 'micro', '1m', 'long')
                # Short
                if (not self.trades['micro']['5m']['trade']['RSI'] and
                    not self.trades['micro']['1m']['trade']['RSI'] and
                    not self.trades['short']['15m']['trade']['RSI'] and
                    not self.trades['short']['30m']['trade']['RSI'] and
                    not self.trades['medium']['1h']['trade']['RSI'] and
                    not self.trades['medium']['4h']['trade']['RSI']) and (
                        not self.trades['short']['30m']['trade']['Momentum']):
                    self.show_results('Iniciado', testing, 'micro', '1m', 'short')
        else:
            self.trade['max'] = (self.trades['micro']['1m']['trade']['close'] if (
                    self.trades['micro']['1m']['trade']['close'] > self.trade['max']) else
                                 self.trade['max'])
            self.trade['min'] = (self.trades['micro']['1m']['trade']['close'] if (
                    self.trades['micro']['1m']['trade']['close'] < self.trade['min']) else
                                 self.trade['min'])
            self.evaluate_operative(testing)

    def save_trade(self, size, last_row):
        length = get_type_trade(size, self.trades)

        self.trades[length][size]['fingerprint'] = last_row['time']
        self.trades[length][size]['last_minute'] = datetime.datetime.strptime(
            str(self.trades['micro']['1m']['fingerprint']), '%Y-%m-%d %H:%M:%S').minute
        self.trades[length][size]['trend'] = last_row['trend']
        self.trades[length][size]['trade']['high'] = last_row['high']
        self.trades[length][size]['trade']['low'] = last_row['low']
        self.trades[length][size]['trade']['close'] = last_row['close']
        self.trades[length][size]['trade']['RSI'] = last_row['RSIs']
        self.trades[length][size]['trade']['RSIs'] = last_row['RSI_ups']
        self.trades[length][size]['trade']['RSI_value'] = last_row['RSI']
        self.trades[length][size]['trade']['mean_f'] = last_row['fast']
        self.trades[length][size]['trade']['mean_f_ups'] = last_row['fast_ups']
        self.trades[length][size]['trade']['Momentum'] = last_row['momentums']
        self.trades[length][size]['trade']['Momentums'] = last_row['momentum_ups']
        self.trades[length][size]['trade']['Momentum_value'] = last_row['momentum']
        self.trades[length][size]['trade']['confirm_dir'] = last_row['avg']
        self.trades[length][size]['trade']['confirm_dir_ups'] = last_row['price_up']
        self.trades[length][size]['trade']['variation'] = last_row['close_variation']
        self.trades[length][size]['trade']['time'] = last_row['mom_t']
        self.trades[length][size]['trade']['ema'] = last_row['buy_ema']
        self.trades[length][size]['trade']['ema_value'] = last_row['mean_close_55']

    def get_market_graphs(self, bot=None, cid=None):

        for size, options in configuration.items():
            try:
                # Get Data
                data = get_binance_symbol_data(symbol=self.symbol, kline_size=size, auto_increment=False,
                                               save=True, sma=options['days'])
                # Analyse
                options['data'] = analysis(df=data, ma_f=options['sma_f'], ma_s=options['sma_s'])
                save_extracted_data(symbol=self.symbol, df=options['data'], form='sma-%s' % options['days'],
                                    size=size)
                # options['min_max'] = get_stats(df=self.data)
                df = options['data'].tail(120)
                if len(df.index) > options['plot']:
                    options['support'], options['resistance'] = supres(df['close'].to_numpy(), options['plot'])
                    # Visualize data
                    plot_df(values=options['plot'], size=size, form='sma-%s' % options['days'],
                            symbol=self.symbol, support=options['support'], resistence=options['resistance'])

                    # Send results
                    photo = open(get_file_name(self.symbol, size, 'sma-%s' % options['days'], 'png'), 'rb')
                    if bot is not None:
                        send_message(cid=cid, text=size, play=False)
                        bot.send_photo(cid, photo)
            except Exception as e:
                print('Error PLOT: ', e)

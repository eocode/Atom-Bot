import time

import pandas as pd
from bot.connect.message_connector import send_message
from bot.connect.thread_connector import limit, async_fn
from modules.core.data.bot_system import system
from modules.financing.crypto.configuration import configuration
from modules.financing.crypto.extractor import get_binance_symbol_data, save_extracted_data, \
    get_file_name, get_type_trade, get_last_row_dataframe_by_time
from modules.financing.crypto.logging import logging_changes, send_messages, notify
from modules.financing.crypto.processing import analysis, plot_df, supres, download_test_data, load_test_data, \
    save_result
import datetime
from modules.financing.crypto.strategies.strategy_configuration import strategy_selector
from modules.financing.crypto.trades import trades
from modules.financing.crypto.utilities import check_if_update, trade_variation, elapsed_time, profit
import os
from dotenv import load_dotenv

load_dotenv()


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

        self.effectivity = {
            'earn': {
                'long': {
                    'operations': 0,
                    'difference': 0,
                },
                'short': {
                    'operations': 0,
                    'difference': 0,
                }
            },
            'lose': {
                'long': {
                    'operations': 0,
                    'difference': 0,
                },
                'short': {
                    'operations': 0,
                    'difference': 0,
                }
            }
        }

        self.result_indicators = ['time', 'Local', 'Action', 'Temp', 'Operative', 'Value', 'Profit', 'Result',
                                  'Risk', 'Time', 'Elapsed', 'MinDif', 'MaxDif', 'Min', 'Max']
        self.strategy = strategy_selector[os.environ["strategy"]]
        self.trades = trades[self.crypto]
        self.testing = []
        self.chat_ids = []

    @limit(1)
    @async_fn
    def start(self, chat_ids=None):
        if not self.process_is_started:
            self.chat_ids = chat_ids
            self.make_simulation(download=True)
            send_messages(trade=self.trade, chat_ids=self.chat_ids, message="Monitoreando %s " % self.crypto)
            self.process_is_started = True
            while True:
                try:
                    updatable = False
                    for size, options in configuration.items():
                        update = check_if_update(size=size, crypto=self.crypto)
                        if update or updatable:
                            data = get_binance_symbol_data(symbol=self.symbol, kline_size=size, auto_increment=False,
                                                           save=False, sma=options['days_s'])
                            options['data'] = analysis(df=data, ma_f=options['sma_f'], ma_s=options['sma_s'])
                            df = options['data'].tail(365)
                            last_row = df.iloc[-1, :]
                            self.update_indicators(last_row=last_row, size=size)
                            logging_changes(size, self.crypto)
                            if size == self.strategy['update_size']:
                                updatable = True
                        time.sleep(2)
                    self.decide(testing=False)
                    self.first_iteration = True
                except Exception as e:
                    print('Error: ', e)
        else:
            send_messages(trade=self.trade, chat_ids=self.chat_ids, message="Monitoreando %s " % self.crypto)
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
                self.update_indicators(last_row=row, size='1m')
                self.update_indicators(last_row=get_last_row_dataframe_by_time(self.trades, '3m', row['timestamp']),
                                       size='3m')
                self.update_indicators(last_row=get_last_row_dataframe_by_time(self.trades, '5m', row['timestamp']),
                                       size='5m')
                self.update_indicators(last_row=get_last_row_dataframe_by_time(self.trades, '15m', row['timestamp']),
                                       size='15m')
                self.update_indicators(last_row=get_last_row_dataframe_by_time(self.trades, '30m', row['timestamp']),
                                       size='30m')
                self.update_indicators(last_row=get_last_row_dataframe_by_time(self.trades, '1h', row['timestamp']),
                                       size='1h')
                self.update_indicators(last_row=get_last_row_dataframe_by_time(self.trades, '4h', row['timestamp']),
                                       size='4h')
                self.update_indicators(last_row=get_last_row_dataframe_by_time(self.trades, '1d', row['timestamp']),
                                       size='1d')
                self.update_indicators(last_row=get_last_row_dataframe_by_time(self.trades, '1w', row['timestamp']),
                                       size='1w')
                self.decide(testing=True)
            df = pd.DataFrame(self.testing, columns=self.result_indicators)

            df.to_csv('backtesting/trades_%s.csv' % self.symbol, index=False)
            save_result(df=df, symbol=self.symbol, crypto=self.crypto)
            self.show_stats()
            self.show_operative()

        except Exception as e:
            print('Error: ', e)

    def decide(self, testing=False):
        if not self.operative:
            trade_operative, start = self.strategy['execute'](self.crypto)
            if start:
                self.operative = True
                self.save_trade('micro', '1m',
                                self.trades['micro']['1m']['trade']['close'],
                                trade_operative)
                notify(testing=testing, message='Iniciado', action='Abrir', trade=self.trade, crypto=self.crypto,
                       profit=profit(self.trade, self.crypto), save=self.testing, chat_ids=self.chat_ids,
                       effectivity=self.effectivity)
        else:
            self.trade['max'] = (self.trades['micro']['1m']['trade']['close'] if (
                    self.trades['micro']['1m']['trade']['close'] > self.trade['max']) else
                                 self.trade['max'])
            self.trade['min'] = (self.trades['micro']['1m']['trade']['close'] if (
                    self.trades['micro']['1m']['trade']['close'] < self.trade['min']) else
                                 self.trade['min'])
            close = self.strategy['evaluate'](trade=self.trade, crypto=self.crypto)
            if close:
                self.operative = False
                notify(testing=testing, message='Cierre', action='Cerrar', trade=self.trade, crypto=self.crypto,
                       profit=profit(self.trade, self.crypto), save=self.testing, chat_ids=self.chat_ids,
                       effectivity=self.effectivity)

    def update_indicators(self, size, last_row):
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

    def save_trade(self, temp, size, close, operative):
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
                    self.trade['last_time'],
                    ' 🟢 ' if self.trade['operative'] == 'long' else ' 🔴 ',
                    self.trade['risk'])
                message += "Inicial: %s - Actual: %s \n" % (
                    self.trade['value'], self.trades['micro']['1m']['trade']['close'])
                message += "Resultado: %s con %s\n\nStats\n" % (
                    profit(trade=self.trade, crypto=self.crypto),
                    trade_variation(current=self.trades['micro']['1m']['trade']['close'], trade=self.trade))

                message += "Tiempo: %s hrs\n" % (elapsed_time(trade=self.trade, crypto=self.crypto, current=True))
                message += "Máximo: %s con %s\n" % (
                    round(self.trade['max']),
                    trade_variation(trade=self.trade, current=round(self.trade['max'])))
                message += "Minimo: %s con %s\n\n" % (
                    round(self.trade['min']),
                    trade_variation(trade=self.trade, current=round(self.trade['min'])))
                message += "%s de %s hrs con %s periodos" % (
                    ('Long' if self.trades['short']['30m']['trade']['Momentum'] else 'Short'),
                    ((self.trades['short']['30m']['trade']['Momentums']) * 30) / 60,
                    self.trades['short']['30m']['trade']['Momentums'])
            else:
                message = "No hay ninguna operativa para %s actualmente" % self.symbol
        else:
            message = "Primero se debe iniciar el proceso de monitoreo para %s" % self.symbol
        send_messages(trade=self.trade, chat_ids=self.chat_ids, message=message)

    @limit(1)
    @async_fn
    def show_stats(self):
        total_operations = (
                (self.effectivity['earn']['long']['operations'] + self.effectivity['earn']['short']['operations']) +
                (self.effectivity['lose']['short']['operations'] + self.effectivity['lose']['long']['operations']))
        total_variation = (
                (self.effectivity['earn']['long']['difference'] + self.effectivity['earn']['short']['difference']) -
                (self.effectivity['lose']['short']['difference'] + self.effectivity['lose']['long']['difference']))
        earn_operations = (
                self.effectivity['earn']['long']['operations'] + self.effectivity['earn']['short']['operations'])
        earn_differences = (
                self.effectivity['earn']['long']['difference'] + self.effectivity['earn']['short']['difference'])
        lose_operations = (
                self.effectivity['lose']['long']['operations'] + self.effectivity['lose']['short']['operations'])
        lose_differences = (
                self.effectivity['lose']['long']['difference'] + self.effectivity['lose']['short']['difference'])
        message = "Eficiencia en %s\n\n" % self.crypto
        message += "Ganancias:\nTrades %s con %s\n" % (
            round(earn_operations, 2), round((earn_operations * 100) / total_operations, 2))
        message += "Variación: %s con %s\n\n" % (
            round(earn_differences, 2), round((earn_differences * 100) / total_variation, 2))
        message += "Perdidas:\nTrades %s con %s\n" % (
            round(lose_operations, 2), round((lose_operations * 100) / total_operations, 2))
        message += "Variación: %s con %s\n" % (
            round(lose_differences, 2), round((lose_differences * 100) / total_variation, 2))

        send_messages(trade=self.trade, chat_ids=self.chat_ids, message=message)

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

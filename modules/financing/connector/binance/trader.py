import pandas as pd
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
        self.trade_type = 'micro'
        self.operative = False
        self.trade = {
            'temp': None,
            'operative': None,
            'value': 0,
            'keep': None
        }
        self.testing = []

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

    def download_test_data(self, cid):
        try:
            self.show_message('Descargando datos de prueba', cid, False)

            for time, options in self.configuration.items():
                # Get Data
                data = get_binance_symbol_data(symbol=self.symbol, kline_size=time, auto_increment=False,
                                               save=True, sma=options['days_t'])
                # Analyse
                options['data'] = analysis(df=data, ma_f=options['sma_f'],
                                           ma_s=options['sma_s'],
                                           mas=options['smas'], time=time)
                save_extracted_data(symbol=self.symbol, df=options['data'], form='sma-%s' % options['days_t'],
                                    size=time)
        except Exception as e:
            print('Error: ', e)
        df = pd.read_csv(get_file_name(self.symbol, '1m',
                                       'sma-%s' % '15'))
        new = df[
            ['timestamp', 'mean_f_diff_res', 'ema_f_ups', 'DIFF', 'ups', 'positive_momentum', 'momentum',
             'momentum_ups', 'buy_ema',
             'RSI', 'positive_RSI', 'RSI_ups',
             'close', 'open', 'last_close', 'close_variation']].copy()
        new.to_csv('test.csv', index=False)

        self.show_message('Datos descargados', cid, False)

    def load_test_data(self, cid):
        self.show_message('Cargando datos', cid, False)
        for time, options in self.configuration.items():
            self.trades[self.get_type_trade(time)][time]['data'] = pd.read_csv(get_file_name(self.symbol, time,
                                                                                             'sma-%s' % options[
                                                                                                 'days_t']))
        self.show_message('Los datos se cargaron', cid, False)

    def make_simulation(self, cid):
        try:
            # Get Test Data
            self.load_test_data(cid)

            main = self.trades[self.get_type_trade('1m')]['1m']['data']
            main = main[main['timestamp'] > '2022-02-08']
            self.process_is_started = True
            self.first_iteration = True

            self.show_message('Realizando backtesting', cid, False)
            for index, row in main.iterrows():
                self.market_sentiment(row, '1m', [], [])
                self.market_sentiment(self.get_last_row_dataframe_by_time('5m', row['timestamp']), '5m', [], [])
                self.market_sentiment(self.get_last_row_dataframe_by_time('15m', row['timestamp']), '15m', [], [])
                self.market_sentiment(self.get_last_row_dataframe_by_time('30m', row['timestamp']), '30m', [], [])
                self.market_sentiment(self.get_last_row_dataframe_by_time('1h', row['timestamp']), '1h', [], [])
                self.market_sentiment(self.get_last_row_dataframe_by_time('4h', row['timestamp']), '4h', [], [])
                self.market_sentiment(self.get_last_row_dataframe_by_time('1d', row['timestamp']), '1d', [], [])
                self.market_sentiment(self.get_last_row_dataframe_by_time('1w', row['timestamp']), '1w', [], [])
                self.take_decision(cid=cid, play=False, testing=True)

            df = pd.DataFrame(self.testing,
                              columns=['time', 'Action', 'Temp', 'Operative', 'Value', 'Ema', 'Profit', 'Result'])

            df.to_csv('processing.csv', index=False)
            df = df[df['Result'] != 'Iniciado']
            df_new = df.groupby('Result')['Profit'].agg(['sum', 'count']).reset_index(drop=False)
            total = df_new['count'].sum()
            df_new['%'] = (df_new['count'] * 100) / total
            df_new = df_new.round(2)
            df_new.to_csv('result.csv', index=False)

            self.show_message('Proceso concluído', cid, False)

        except Exception as e:
            print('Error: ', e)

    def get_last_row_dataframe_by_time(self, time, limiter):
        data = self.trades[self.get_type_trade(time)][time]['data']
        return data[data['timestamp'] <= limiter].iloc[-1, :]

    def save_operative(self, temp, time, close, operative):
        self.trade['temp'] = temp
        self.trade['operative'] = operative
        self.trade['time'] = time
        self.trade['value'] = close

    def show_results(self, cid, play, time_sup, time_inf, temp, operative, message, testing):
        self.operative = True
        self.save_operative(temp, time_inf, self.trades[temp][time_inf]['trade']['close'], operative)
        if not testing:
            self.show_message(message=message, cid=cid, play=play)
            self.get_resume(temp, time_sup, time_inf, cid)
        else:
            row = [self.trades[temp][time_inf]['fingerprint'], 'Open', temp, operative,
                   self.trades[temp][time_inf]['trade']['close'],
                   self.trades[temp][time_inf]['trade']['ema_value'], 0, 'Iniciado']
            self.testing.append(row)

    def evaluate_operative(self, testing, cid, play):
        type = None
        close = False
        if self.trade['temp'] == 'micro':
            if self.trade['operative'] == 'long':
                if ((not self.trades['micro']['1m']['trade']['mean_f']) and (
                        not self.trades['micro']['5m']['trade']['RSI'])) or (
                        (self.trades['micro']['5m']['trade']['RSI_value'] > 77) and (
                        not self.trades['micro']['5m']['trade']['RSI'])):
                    type = 'Long'
                    close = True
            else:
                if (self.trades['micro']['1m']['trade']['mean_f'] and (self.trades['micro']['5m']['trade']['RSI'])) or (
                        (self.trades['micro']['5m']['trade']['RSI_value'] < 23) and (
                        self.trades['micro']['5m']['trade']['RSI'])):
                    type = 'Short'
                    close = True
        if close:
            self.operative = False
            if not testing:
                self.show_message(message='Cerrar %s en %s' % (type, self.trades['micro']['1m']['trade']['close']),
                                  cid=cid, play=play)
            else:
                if self.trade['operative'] == 'long':
                    diff = float(self.trades[self.trade['temp']]['1m']['trade']['close']) - (float(self.trade['value']))
                else:
                    diff = (float(self.trade['value'])) - float(self.trades[self.trade['temp']]['1m']['trade']['close'])
                win = 'Ganado' if diff > 0 else 'Perdido'
                row = [self.trades[self.trade['temp']]['1m']['fingerprint'], 'Close', self.trade['temp'],
                       self.trade['operative'],
                       self.trades[self.trade['temp']]['1m']['trade']['close'],
                       round(self.trades[self.trade['temp']]['1m']['trade']['ema_value'], 2), round(diff, 2), win
                       ]
                self.testing.append(row)

    def take_decision(self, cid=None, play=False, testing=False):
        # Micro Trade
        if not self.operative:
            if self.trade_type == 'micro':
                # Long
                if (self.trades['micro']['1m']['trade']['mean_f']) and (
                        self.trades['micro']['1m']['trade']['Momentum']) and (
                        not self.trades['micro']['1m']['trade']['time']) and (
                        self.trades['medium']['1h']['trade']['mean_f']) and (
                        self.trades['medium']['4h']['trade']['Momentum']) and (
                        self.trades['micro']['5m']['trade']['Momentum']) and (
                        self.trades['medium']['1h']['trade']['RSI']) and (
                        self.trades['micro']['1m']['trade']['confirm_dir'] and
                        self.trades['micro']['1m']['trade']['confirm_dir_ups'] > 1):
                    if not self.trades['short']['15m']['trade']['Momentum']:
                        m = 'Riesgo alto'
                    else:
                        m = 'Riesgo bajo'
                    self.show_results(cid, play, '5m', '1m', 'micro', 'long', 'Micro Long - %s' % m, testing)
                # Short
                if (not self.trades['micro']['1m']['trade']['mean_f']) and (
                        not self.trades['micro']['1m']['trade']['Momentum']) and (
                        self.trades['micro']['1m']['trade']['time']) and (
                        not self.trades['medium']['1h']['trade']['mean_f']) and (
                        not self.trades['medium']['4h']['trade']['Momentum']) and (
                        not self.trades['micro']['5m']['trade']['Momentum']) and (
                        not self.trades['medium']['1h']['trade']['RSI']) and (
                        not self.trades['micro']['1m']['trade']['confirm_dir'] and
                        self.trades['micro']['1m']['trade']['confirm_dir_ups'] > 1):
                    if self.trades['short']['15m']['trade']['Momentum']:
                        m = 'Riesgo alto'
                    else:
                        m = 'Riesgo bajo'
                    self.show_results(cid, play, '5m', '1m', 'micro', 'short', 'Micro Short - %s' % m, testing)
        else:
            self.evaluate_operative(testing, cid, play)

    def get_full_resumes(self, cid=None):
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

        if cid is not None:
            send_message(cid, message)
        else:
            print(message)

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
            return False
        else:
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
            self.trades[type][time]['trade']['RSI_value'] = last_row['RSI']
            self.trades[type][time]['trade']['last_RSI_value'] = last_row['RSI_rv']
            self.trades[type][time]['trade']['RSIs'] = last_row['RSI_ups']
            self.trades[type][time]['trade']['mean_f'] = last_row['mean_f_diff_res']
            self.trades[type][time]['trade']['Momentum'] = last_row['positive_momentum']
            self.trades[type][time]['trade']['Momentums'] = last_row['momentum_ups']
            self.trades[type][time]['trade']['confirm_dir'] = last_row['DIFF']
            self.trades[type][time]['trade']['confirm_dir_ups'] = last_row['ups']
            self.trades[type][time]['trade']['variation'] = last_row['close_variation']
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

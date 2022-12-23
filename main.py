from binance.client import Client
import talib as ta
import numpy as np
from datetime import datetime
import decimal
import time
import os
import sys
from telegram import *
from telegram.ext import *
from telegram.ext import CommandHandler, CallbackContext, Updater


print('\n Starting application...')

filename = 'credentials.txt'
filename_settings = 'settings.txt'

lines_set = [line_set.rstrip('\n') for line_set in open(filename_settings)]


# TELEGRAM
lines = [line.rstrip('\n') for line in open(filename)]
user_id = lines[4]
updater = Updater(token=lines[5], use_context=True)
dispatcher = updater.dispatcher


def function_reset(update, context):
    reset_app = "Applicatie word opnieuw opgestart"
    context.bot.send_message(chat_id=update.message.chat.id, text=reset_app)
    os.execv(sys.executable, ['python'] + sys.argv)


def function_help(update, context):
    msg = "/1m - 1m interval\n/3m - 3m interval\n/btc - Coinpair BTC\n/busd - Coinpair BUSD\n\n/settings - Instellingen\n/help - Help\n/reset - Reset script"
    context.bot.send_message(chat_id=update.message.chat.id, text=msg)
    

def function_settings_all(update, context):
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    context.bot.send_message(chat_id=update.message.chat.id, text=f'Interval is: {data[1]}\nCoinpair is: {data[3]}')


def function_settings_1m(update, context):
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    data[1] = '1\n'
    with open('settings.txt', 'w') as file:
        file.writelines( data )
    context.bot.send_message(chat_id=update.message.chat.id, text='Interval is nu: 1m')
        

def function_settings_3m(update, context):
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    data[1] = '3\n'
    with open('settings.txt', 'w') as file:
        file.writelines( data )
    context.bot.send_message(chat_id=update.message.chat.id, text='Interval is nu: 3m')
        

def function_settings_btc(update, context):
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    data[3] = 'btc\n'
    with open('settings.txt', 'w') as file:
        file.writelines( data )
    context.bot.send_message(chat_id=update.message.chat.id, text='Coinpair is nu: BTC')
        

def function_settings_busd(update, context):
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    data[3] = 'busd\n'
    with open('settings.txt', 'w') as file:
        file.writelines( data )
    context.bot.send_message(chat_id=update.message.chat.id, text='Coinpair is nu: BUSD')
        

dispatcher.add_handler(CommandHandler("1m", function_settings_1m))
dispatcher.add_handler(CommandHandler("3m", function_settings_3m))
dispatcher.add_handler(CommandHandler("btc", function_settings_btc))
dispatcher.add_handler(CommandHandler("busd", function_settings_busd))
dispatcher.add_handler(CommandHandler('help', function_help))
dispatcher.add_handler(CommandHandler('settings', function_settings_all))
dispatcher.add_handler(CommandHandler('reset', function_reset))
updater.start_polling()


def function_count():
    symbol_list = function_symbol()
    for i in range(len(symbol_list)):
        if symbol_list[i] == 'restart':
            os.execv(sys.executable, ['python'] + sys.argv)     # restarts application

        symbol = symbol_list[i]
        starttime = '1 day ago UTC'  # to start for 1 day ago
        interval_num = lines_set[1]
        interval_let = "m"
        interval = str(interval_num) + interval_let
        klines = trader.client.get_historical_klines(symbol, interval, starttime)
        # klines = trader.client.get_historical_klines("RADBUSD", "1m", "20-12-2022", "21-12-2022 07:18:00 UTC, ")
        volume = trader.client.get_ticker(symbol=symbol)['quoteVolume']

        open_time = [int(entry[0]) for entry in klines]
        open = [float(entry[1]) for entry in klines]
        high = [float(entry[2]) for entry in klines]
        low = [float(entry[3]) for entry in klines]
        close = [float(entry[4]) for entry in klines]
        high_array = np.asarray(high)
        low_array = np.asarray(low)
        close_array = np.asarray(close)
        new_time = [datetime.fromtimestamp(time/1000) for time in open_time]

        macd, macdsignal, macdhist = ta.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)
        slowk, slowd = ta.STOCH(high_array, low_array, close_array, fastk_period=14, slowk_period=1, slowk_matype=0, slowd_period=3, slowd_matype=0)
        psar = ta.SAR(high_array, low_array, acceleration=0.02, maximum=0.2)
        ma200 = ta.MA(close_array, 200)
        ma50 = ta.MA(close_array, 50)
        ma20 = ta.MA(close_array, 20)
        st = ta.STDDEV(close_array, timeperiod=20, nbdev=1)

        upper_bb = (ma20[-1] + 2 * st[-1])
        lower_bb = (ma20[-1] - 2 * st[-1])

        # candle gesloten onder de lower bb?
        if decimal.Decimal(close_array[-1]) < decimal.Decimal(lower_bb):
            msg = f'🟡 {symbol}: 1. Close is correct'
            print(msg)
        else:
            msg = f'🔴 {symbol}: 1. Close is fout'
            # print(msg)
            continue

        # Stoch check
        if slowd[-1] < 20 and slowk[-1] < 20:
            msg = f'🟡 {symbol}: 2. Stoch is correct'
            print(msg)
        else:
            msg = f'🔴 {symbol}: 2. Stoch is fout'
            print(msg)
            continue
        
        # volume check
        if symbol[-3:] == 'BTC':
            if decimal.Decimal(volume) > 100:
                msg = f'🟡 {symbol}:3.  Volume is correct'
                print(msg)
            else:
                msg = f'🔴 {symbol}: 3. Volume is fout'
                print(msg)
                continue
        if symbol[-3:] == 'USD':
            if decimal.Decimal(volume) > 5000000:
                msg = f'🟡 {symbol}: 3. Volume is correct'
                print(msg)
            else:
                msg = f'🔴 {symbol}: 3. Volume is fout'
                print(msg)
                continue
        
        # BB check
        calc_percentage = ((decimal.Decimal(upper_bb) - decimal.Decimal(lower_bb)) / ((decimal.Decimal(upper_bb) + decimal.Decimal(lower_bb)) /2) * 100)
        if calc_percentage > 1.3 and calc_percentage < 5:
            msg = f"🟡 {symbol}: 4. BB is correct: {calc_percentage}"
            print(msg)
            updater.bot.send_message(chat_id=user_id, text=msg)
        else:
            msg = f'🔴 {symbol}: 4. BB is fout'
            print(msg)
            continue
        
        # PSAR check
        if (decimal.Decimal(psar[-1]) < decimal.Decimal(ma20[-1]) or 
            decimal.Decimal(psar[-2]) < decimal.Decimal(ma20[-2]) or
            decimal.Decimal(psar[-3]) < decimal.Decimal(ma20[-3])):
            msg = f'🟡 {symbol}: 5. PSAR is correct'
            print(msg)
            updater.bot.send_message(chat_id=user_id, text=msg)
        else:
            msg = f'🔴 {symbol}: 5. PSAR is fout'
            print(msg)
            continue

        # MA's check
        if ma200[-1] > ma50[-1] and ma50[-1] > ma20[-1]:
            ma200_ma50_calc = abs((ma200[-1] - ma50[-1]) / ((ma200[-1] + ma50[-1]) / 2) * 100)
            if ma200_ma50_calc > 0.3:  # 1
                ma50_ma20_calc = abs((ma50[-1] - ma20[-1]) / ((ma50[-1] + ma20[-1]) / 2) * 100)
                if ma50_ma20_calc > 0.3:  # 0.7
                    print('Alle MA lijnen staan goed met de juiste percentages.')
                    msg = f"🟡 {symbol}: 6. MA'S zijn correct"
                    updater.bot.send_message(chat_id=user_id, text=msg)
                else:
                    msg = f'🔴 {symbol}: 6. MA is fout'
                    print(msg)
                    continue
            else:
                msg = f'🔴 {symbol}: 6. MA is fout'
                print(msg)
                continue
        else:
            msg = f'🔴 {symbol}: 6. MA is fout'
            print(msg)
            continue
        
        # loop functie, 60 seconden x 3 candles x interval
        end_macd_loop = time.time() + 60 * float(interval_num) * 3
        while time.time() < end_macd_loop:
            # MACD check
            macd_now = (decimal.Decimal(macd[-1]) - decimal.Decimal(macdsignal[-1]))
            macd_old = (decimal.Decimal(macd[-2]) - decimal.Decimal(macdsignal[-2]))
            if decimal.Decimal(macd[-1]) < decimal.Decimal(macdsignal[-1]):
                if macd_now > macd_old:
                    # get ask price
                    ask_price = trader.client.get_orderbook_ticker(symbol=symbol)
                    print(ask_price['askPrice'])
                    msg = f"🟢 Alle voorwaarden behaald!\nAsk price: {ask_price['askPrice']}"
                    print(msg)
                    updater.bot.send_message(chat_id=user_id, text=msg)
                    os.execv(sys.executable, ['python'] + sys.argv)
                    time.sleep(3)
                    break
        msg = f'🔴 {symbol}: 7. MACD is fout'
        print(msg)
        os.execv(sys.executable, ['python'] + sys.argv)
        time.sleep(3)
        break


def function_symbol():
    if lines_set[3] == 'BTC' or lines_set[3] == 'btc' or lines_set[3] == 'Btc':
        symbol_list = ['ALGOBTC', 'ATOMBTC', 'AVAXBTC', 'AXSBTC', 'BNBBTC', 'DOTBTC', 'EGLDBTC', 'ETHBTC',
                       'DOGEBTC', 'FILBTC', 'FTMBTC', 'LINKBTC', 'LTCBTC', 'MANABTC', 'MATICBTC', 'NEOBTC',
                       'RUNEBTC', 'SANDBTC', 'SOLBTC', 'THETABTC', 'XLMBTC', 'XMRBTC', 'XRPBTC', 'restart']

    if lines_set[3] == 'BUSD' or lines_set[3] == 'busd' or lines_set[3] == 'Busd':
        symbol_list = ['SHIBBUSD', 'LUNCBUSD', 'BTTCBUSD', 'XECBUSD', 'LEVERBUSD', 'WINBUSD', 'DOGEBUSD', 'EPXBUSD',
                       'JASMYBUSD', 'USTCBUSD', 'MBLBUSD', 'IQBUSD', 'REEFBUSD', 'XRPBUSD', 'RSRBUSD', 'GALABUSD',
                       'SPELLBUSD', 'XVGBUSD', 'POWRBUSD', 'SLPBUSD', 'ADABUSD', 'OOKIBUSD', 'DENTBUSD', 'VIBBUSD',
                       'TRXBUSD', 'AMBBUSD', 'HOTBUSD', 'VETBUSD', 'SCBUSD', 'LOOMBUSD', 'STMXBUSD', 'GTOBUSD', 'CHZBUSD',
                       'ROSEBUSD', 'SRMBUSD', 'ACHBUSD', 'TLMBUSD', 'QIBUSD', 'DGBBUSD', 'WAXPBUSD', 'STPTBUSD', 'SUNBUSD',
                       'LINABUSD', 'VIDTBUSD', 'POLYXBUSD', 'MATICBUSD', 'ANCBUSD', 'CKBBUSD', 'PEOPLEBUSD', 'COSBUSD',
                       'AERGOBUSD', 'CVCBUSD', 'ONEBUSD', 'AGIXBUSD', 'FORBUSD', 'FTMBUSD', 'ALGOBUSD', 'TBUSD', 'ZILBUSD',
                       'HBARBUSD', 'TROYBUSD', 'TKOBUSD', 'GMTBUSD', 'KEYBUSD', 'MTLBUSD', 'HIVEBUSD', 'FETBUSD', 'HFTBUSD',
                       'AMPBUSD', 'OCEANBUSD', 'UFTBUSD', 'EURBUSD', 'QKCBUSD', 'TVKBUSD', 'IOSTBUSD', 'MAGICBUSD', 'AUDBUSD',
                       'XLMBUSD', 'RVNBUSD', 'VITEBUSD', 'PONDBUSD', 'HOOKBUSD', 'GLMBUSD', 'DODOBUSD', 'GRTBUSD', 'LSKBUSD',
                       'AKROBUSD', 'SNTBUSD', 'PHBBUSD', 'MDXBUSD', 'SNMBUSD', 'CELRBUSD', 'MOBBUSD', 'ARKBUSD', 'SANDBUSD',
                       'RAYBUSD', 'TFUELBUSD', 'TWTBUSD', 'CTXCBUSD', 'NEARBUSD', 'ATABUSD', 'OPBUSD', 'MIRBUSD', 'MDTBUSD',
                       'PROSBUSD', 'RENBUSD', 'APTBUSD', 'DYDXBUSD', 'DOCKBUSD', 'STORJBUSD', 'RADBUSD', 'SKLBUSD', 'FTTBUSD',
                       'ELFBUSD', 'CHRBUSD', 'PHABUSD', 'RUNEBUSD', 'MASKBUSD', 'FIDABUSD', 'MANABUSD', 'APEBUSD', 'SYSBUSD',
                       'TRIBEBUSD', 'ANKRBUSD', 'restart']
    return symbol_list


class Trader:
    def __init__(self, file):
        self.connect(file)

    def connect(self, file):
        lines = [line.rstrip('\n') for line in open(file)]
        key = lines[1]
        secret = lines[2]
        self.client = Client(key, secret)

    def getBalances(self):
        prices = self.client.get_widraw_history()
        return prices

trader = Trader(filename)

function_count()

from binance.client import Client
import talib as ta
import numpy as np
import pandas as pd
from datetime import datetime
import decimal
import time
import os
import platform
import sys
import csv
import requests
import urllib.request


print('\n Starting application...')

filename = 'credentials.txt'
filename_settings = 'settings.txt'
lines_set = [line_set.rstrip('\n') for line_set in open(filename_settings)]

lines_cred = [line_cred.rstrip('\n') for line_cred in open(filename)]
user_id = lines_cred[4]
telegram_api = lines_cred[5]

def function_sendmessage(msg):
    apiURL = f'https://api.telegram.org/bot{telegram_api}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': user_id, 'text': msg})
        print(response.text)
        return
    except Exception as e:
        print(e)
        return


def function_sendfile():
    fPath = "/home/pi/binancebot/trades.csv"
    apiURL = f'https://api.telegram.org/bot{telegram_api}/sendDocument'
    try:
        files = {'document': open(fPath, 'rb')}
        params = {'chat_id': user_id}
        response = requests.post(apiURL, params=params, files=files)
        print(response.text)
        return
    except Exception as e:
        print(e)
        return


def function_sendchart():
    fPath = "/home/pi/binancebot/chart.jpg"
    apiURL = f'https://api.telegram.org/bot{telegram_api}/sendPhoto'
    try:
        files = {'photo': open(fPath, 'rb')}
        params = {'chat_id': user_id}
        response = requests.post(apiURL, params=params, files=files)
        print(response.text)
        return
    except Exception as e:
        print(e)
        return


def function_reset():
    msg = "Applicatie word opnieuw opgestart"
    function_sendmessage(msg)
    os.execv(sys.executable, ['python'] + sys.argv)


def function_help():
    msg = "/1m - 1m interval\n/3m - 3m interval\n/btc - Coinpair BTC\n/busd - Coinpair BUSD\n\n/settings - Instellingen\n/trades Overzicht\n/help - Help\n/reset - Reset script"
    function_sendmessage(msg)


def function_settings_all():
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    msg = f'Interval is: {data[1]}\nCoinpair is: {data[3]}'
    function_sendmessage(msg)


def function_settings_1m():
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    data[1] = '1\n'
    with open('settings.txt', 'w') as file:
        file.writelines( data )
    msg = 'Interval is nu: 1m'
    function_sendmessage(msg)


def function_settings_3m():
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    data[1] = '3\n'
    with open('settings.txt', 'w') as file:
        file.writelines( data )
    msg = 'Interval is nu: 3m'
    function_sendmessage(msg)


def function_settings_btc():
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    data[3] = 'btc\n'
    with open('settings.txt', 'w') as file:
        file.writelines( data )
    msg = 'Coinpair is nu: BTC'
    function_sendmessage(msg)


def function_settings_busd():
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    data[3] = 'busd\n'
    with open('settings.txt', 'w') as file:
        file.writelines( data )
    msg = 'Coinpair is nu: BUSD'
    function_sendmessage(msg)

def function_count():
    symbol_list = function_symbol()
    for i in range(len(symbol_list)):
        if symbol_list[i] == 'reset':
            time.sleep(10)
            if platform.system() == "Windows":
                os.execv(sys.executable, ['python'] + sys.argv)     # restarts application
            else:
                os.system('sudo reboot')
        symbol = symbol_list[i]
        starttime = '1 day ago UTC'  # to start for 1 day ago
        interval_num = lines_set[1]
        interval_let = "m"
        interval = str(interval_num) + interval_let
        klines = trader.client.get_historical_klines(symbol, interval, starttime)

        high = [float(entry[2]) for entry in klines]
        low = [float(entry[3]) for entry in klines]
        close = [float(entry[4]) for entry in klines]
        high_array = np.asarray(high)
        low_array = np.asarray(low)
        close_array = np.asarray(close)

        macd, macdsignal, macdhist = ta.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)
        slowk, slowd = ta.STOCH(high_array, low_array, close_array, fastk_period=14, slowk_period=1, slowk_matype=0, slowd_period=3, slowd_matype=0)
        psar = ta.SAR(high_array, low_array, acceleration=0.02, maximum=0.2)
        ma200 = ta.MA(close_array, 200)
        ma50 = ta.MA(close_array, 50)
        ma20 = ta.MA(close_array, 20)
        st = ta.STDDEV(close_array, timeperiod=20, nbdev=1)

        upper_bb = (ma20[-1] + 2 * st[-1])
        lower_bb = (ma20[-1] - 2 * st[-1])

        write_dict = {'BUY_SELL': '',
                      'Datetime': 'date_time',
                      'Symbol': symbol,
                      'Close': 'Close',
                      'Stoch': 'slowk[-1]',
                      'BBpercentages': 'calc_percentage',
                      'PSAR': 'psar[-1]',
                      'MA200': 'MA200',
                      'MA50': 'MA50',
                      'MA20': 'MA20',
                      'macdhist': 'macdhist',
                      'AskPrice': 'askprice',
                      'Sell': '0',
                      'OrderID': '0'}

        # candle gesloten onder de lower bb?
        if decimal.Decimal(close_array[-1]) < decimal.Decimal(lower_bb):
            msg = f'🟢🔸🔸🔸🔸🔸 {symbol}: 1. Close is correct'
            write_dict['Close'] = "%.8f" % decimal.Decimal(close_array[-1])
            print(msg)
        else:
            msg = f'🔸🔸🔸🔸🔸🔸 {symbol}: 1. Close is fout'
            # print(msg)
            continue

        # Stoch check
        if (slowk[-1] < 20 or
            slowk[-2] < 20):
            msg = f'🟢🟢🔸🔸🔸🔸 {symbol}: 2. Stoch is correct'
            write_dict['Stoch'] = "%.8f" % decimal.Decimal(slowk[-1])
            print(msg)
        else:
            msg = f'🟢🔴🔴🔴🔴🔴 {symbol}: 2. Stoch is fout'
            print(msg)
            continue

        # BB check
        calc_percentage = ((decimal.Decimal(upper_bb) - decimal.Decimal(lower_bb)) / ((decimal.Decimal(upper_bb) + decimal.Decimal(lower_bb)) /2) * 100)
        if calc_percentage > 1 and calc_percentage < 5:
            calc_percentage = "%.2f" % decimal.Decimal(calc_percentage)
            msg = f"🟢🟢🟢🔸🔸🔸 {symbol}: 3. BB is correct: {calc_percentage}%"
            write_dict['BBpercentages'] = calc_percentage
            print(msg)
        else:
            msg = f'🟢🟢🔴🔴🔴🔴 {symbol}: 3. BB is fout'
            print(msg)
            continue

        # PSAR check
        if (decimal.Decimal(psar[-1]) < decimal.Decimal(ma20[-1])):
            msg = f'🟢🟢🟢🟢🔸🔸 {symbol}: 4. PSAR is correct'
            write_dict['PSAR'] = "%.8f" % decimal.Decimal(psar[-1])
            print(msg)
        else:
            msg = f'🟢🟢🟢🔴🔴🔴 {symbol}: 4. PSAR is fout'
            print(msg)
            continue

        # MA's check
        if ma200[-1] > ma50[-1] and ma50[-1] > ma20[-1]:
            ma200_ma50_calc = abs((ma200[-1] - ma50[-1]) / ((ma200[-1] + ma50[-1]) / 2) * 100)
            if ma200_ma50_calc > 0.3:  # 1
                ma50_ma20_calc = abs((ma50[-1] - ma20[-1]) / ((ma50[-1] + ma20[-1]) / 2) * 100)
                if ma50_ma20_calc > 0.3:  # 0.7
                    msg = f"🟢🟢🟢🟢🟢🔸 {symbol}: 5. MA'S zijn correct"
                    write_dict['MA200'] = "%.8f" % decimal.Decimal(ma200[-1])
                    write_dict['MA50'] = "%.8f" % decimal.Decimal(ma50[-1])
                    write_dict['MA20'] = "%.8f" % decimal.Decimal(ma20[-1])
                    print(msg)
                else:
                    msg = f'🟢🟢🟢🟢🔴🔴 {symbol}: 5. MA is fout'
                    print(msg)
                    continue
            else:
                msg = f'🟢🟢🟢🟢🔴🔴 {symbol}: 5. MA is fout'
                print(msg)
                continue
        else:
            msg = f'🟢🟢🟢🟢🔴🔴 {symbol}: 5. MA is fout'
            print(msg)
            continue

        # MACD check
        # loop functie, 60 seconden x 3 candles x interval
        end_macd_loop = (60 * float(interval_num) * 3)
        macd_hist_list = []
        macd_hist_list.append(decimal.Decimal(macdhist[-1]))
        print(f'{macd_hist_list[0]} - Old one')
        t1 = datetime.now()
        while (datetime.now()-t1).seconds <= end_macd_loop:
            klines = trader.client.get_historical_klines(symbol, interval, starttime)
            close = [float(entry[4]) for entry in klines]
            close_array = np.asarray(close)
            macd, macdsignal, macdhist = ta.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)
            macdhist_new = (macd[-1] - macdsignal[-1])
            print(macdhist_new)
            time.sleep(10)
            if decimal.Decimal(macdhist_new) > macd_hist_list[0]:
                if decimal.Decimal(macdhist_new) < 0:
                    now_datetime = datetime.now()
                    date_time = now_datetime.strftime("%d/%m/%Y, %H:%M:%S")
                    # get ask price
                    ask_price = trader.client.get_orderbook_ticker(symbol=symbol)
                    askprice = ask_price['askPrice']
                    print(askprice)
                    msg = f"🟢🟢🟢🟢🟢🟢 {symbol}: Alle voorwaarden behaald!\nAsk price: {askprice}"
                    print(msg)
                    write_dict['Datetime'] = date_time
                    write_dict['macdhist'] = "%.8f" % decimal.Decimal(macdhist_new)
                    write_dict['AskPrice'] = "%.8f" % decimal.Decimal(askprice)
                    # function_sendmessage(msg)
                    function_buy(symbol, write_dict)
        msg = f'🟢🟢🟢🟢🟢🔴 {symbol}: 6. MACD is fout'
        print(msg)
        os.execv(sys.executable, ['python'] + sys.argv)


def function_symbol():
    now_datetime = datetime.now()
    date_time = now_datetime.strftime("%d/%m/%Y, %H:%M:%S")
    timer = time.time() + 60 * 60
    with open('coins.txt', 'r') as f:
        data = f.readlines()
    if not data:
        with open('coins.txt', 'w') as f:
            f.write(f"{time.time()}\n{date_time}\nempty")
        time.sleep(1)
    with open('coins.txt', 'r') as f:
         data = f.readlines()
    if (decimal.Decimal(data[0]) < time.time()) or data[2] == "empty":
        with open('coins.txt', 'w') as f:
            f.write(f"{timer}\n{date_time}\n")
        get_all = trader.client.get_ticker()
        list_symbols_btc = []
        list_symbols_busd = []
        for i in get_all:
            if decimal.Decimal(i['quoteVolume']) > 100 and i['symbol'][-3:] == 'BTC':
                list_symbols_btc.append(i['symbol'])
            if decimal.Decimal(i['quoteVolume']) > 5000000 and i['symbol'][-4:] == 'BUSD':
                list_symbols_busd.append(i['symbol'])
        list_symbols_btc.append("reset")
        list_symbols_busd.append("reset")
        with open('coins.txt', 'a') as f:
            f.write(f"{','.join(list_symbols_btc)}\n{','.join(list_symbols_busd)}")
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    if data[3].strip() == "busd":
        with open('coins.txt', 'r') as f:
            coins = f.readlines()
        symbol_list = coins[3].split(',')
    if data[3].strip() == "btc":
        with open('coins.txt', 'r') as f:
            coins = f.readlines()
        symbol_list = coins[2].split(',')
    return symbol_list


def function_buy(symbol, write_dict):
    balance_btc = trader.client.get_asset_balance(asset='BTC')['free']
    balance_busd = trader.client.get_asset_balance(asset='BUSD')['free']
    ask_price = trader.client.get_orderbook_ticker(symbol=symbol)
    stepsize_client = trader.client.get_symbol_info(symbol)
    stepsize = float(stepsize_client['filters'][1]['stepSize'])
    askprice = float(ask_price['askPrice'])
    with open('settings.txt', 'r') as file:
        data = file.readlines()
    if data[3].strip() == "btc":
        quant = float(balance_btc)
    if data[3].strip() == "busd":
        quant = float(balance_busd)

    buy_calc_amount = (quant / askprice) * 0.98
    sell_calcprice = 0.0025 * askprice + askprice

    if stepsize == 1.00000000:
        buy_amount = "%.0f" % buy_calc_amount
        buy_amount = float(buy_amount)
    elif stepsize == 0.10000000:
        buy_amount = "%.1f" % buy_calc_amount
        buy_amount = float(buy_amount)
    elif stepsize == 0.01000000:
        buy_amount = "%.2f" % buy_calc_amount
        buy_amount = float(buy_amount)
    elif stepsize == 0.00100000:
        buy_amount = "%.3f" % buy_calc_amount
        buy_amount = float(buy_amount)
    elif stepsize == 0.00010000:
        buy_amount = "%.4f" % buy_calc_amount
        buy_amount = float(buy_amount)
    elif stepsize == 0.00001000:
        buy_amount = "%.5f" % buy_calc_amount
        buy_amount = float(buy_amount)
    elif stepsize == 0.00000100:
        buy_amount = "%.6f" % buy_calc_amount
        buy_amount = float(buy_amount)
    elif stepsize == 0.00000010:
        buy_amount = "%.7f" % buy_calc_amount
        buy_amount = float(buy_amount)
    elif stepsize == 0.00000001:
        buy_amount = "%.8f" % buy_calc_amount
        buy_amount = float(buy_amount)
    else:
        buy_amount = "%.0f" % buy_calc_amount
        buy_amount = float(buy_amount)
    order = trader.client.order_market_buy(symbol=symbol, quantity=buy_amount)
    print(order)
    orderid = order['orderId']
    chart_key = lines_cred[7]
    chart_url = f"https://api.chart-img.com/v1/tradingview/advanced-chart?interval=1m&symbol=BINANCE:{symbol}&studies=SAR&studies=BB&studies=MACD&studies=MA:50,close&studies=MA:200,close&key={chart_key}"
    urllib.request.urlretrieve(chart_url, "chart.jpg")
    msg = f"{symbol} buy for: {askprice}\norder ID: {orderid}"
    write_dict['BUY_SELL'] = 'BUY'
    write_dict['OrderID'] = decimal.Decimal(orderid)
    print(write_dict)
    with open('trades.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(write_dict.values())
    function_sendmessage(msg)
    function_sendchart()
    # function_sendfile()
    time.sleep(10)
    function_sell(symbol=symbol, sell_calcprice=sell_calcprice, orderid=orderid)


def function_sell(symbol, sell_calcprice, orderid):
    get_order_status = trader.client.get_order(symbol=symbol, orderId=orderid)
    order_status = get_order_status['status']
    while order_status == "NEW":
        time.sleep(10)

    ticksize_client = trader.client.get_symbol_info(symbol)
    ticksize = float(ticksize_client['filters'][0]['tickSize'])
    if ticksize == 1.00000000:
        sell_price = "%.0f" % sell_calcprice
        sell_price = float(sell_price)
    elif ticksize == 0.10000000:
        sell_price = "%.1f" % sell_calcprice
        sell_price = float(sell_price)
    elif ticksize == 0.01000000:
        sell_price = "%.2f" % sell_calcprice
        sell_price = float(sell_price)
    elif ticksize == 0.00100000:
        sell_price = "%.3f" % sell_calcprice
        sell_price = float(sell_price)
    elif ticksize == 0.00010000:
        sell_price = "%.4f" % sell_calcprice
        sell_price = float(sell_price)
    elif ticksize == 0.00001000:
        sell_price = "%.5f" % sell_calcprice
        sell_price = float(sell_price)
    elif ticksize == 0.00000100:
        sell_price = "%.6f" % sell_calcprice
        sell_price = float(sell_price)
    elif ticksize == 0.00000010:
        sell_price = "%.7f" % sell_calcprice
        sell_price = float(sell_price)
    elif ticksize == 0.00000001:
        sell_price = "%.8f" % sell_calcprice
        sell_price = float(sell_price)
    else:
        sell_price = "%.0f" % sell_calcprice
        sell_price = float(sell_price)

    now_datetime = datetime.now()
    date_time = now_datetime.strftime("%d/%m/%Y, %H:%M:%S")
    coin1 = symbol.replace('BUSD', '')
    coin2 = coin1.replace('BTC', '')
    balance = trader.client.get_asset_balance(asset=coin2)
    total_asset = float(balance['free'])
    order = trader.client.order_limit_sell(symbol=symbol, quantity=total_asset, price=str(sell_price))
    print(order)
    orderid = order['orderId']
    write_dict = {'BUY_SELL': 'SELL',
                  'Datetime': date_time,
                  'Symbol': symbol,
                  'Close': '0',
                  'Stoch': '0',
                  'BBpercentages': '0',
                  'PSAR': '0',
                  'MA200': '0',
                  'MA50': '0',
                  'MA20': '0',
                  'macdhist': '0',
                  'AskPrice': '0',
                  'Sell': float(sell_price),
                  'OrderID': decimal.Decimal(orderid)}
    with open('trades.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(write_dict.values())
    function_checkorder()
    msg = f'{symbol} has been sold.'
    function_sendmessage(msg)
    function_sendfile()
    os.execv(sys.executable, ['python'] + sys.argv)


def function_checkorder():
    data = pd.read_csv("trades.csv")
    last_orderid = data.iloc[-1].OrderID
    last_symbol = data.iloc[-1].Symbol
    while True:
        get_order_status = trader.client.get_order(symbol=last_symbol, orderId=last_orderid)
        order_status = get_order_status['status']
        if order_status == "NEW":
            time.sleep(15)
        else:
            return


def function_checkbtc():
    btc_price = trader.client.get_ticker(symbol="BTCBUSD")
    currentprice = float(btc_price['lastPrice'])
    price_high = ((currentprice / 100) * 1) + currentprice
    price_low = currentprice - ((currentprice / 100) * 1)
    now_datetime = datetime.now()
    date_time = now_datetime.strftime("%d/%m/%Y, %H:%M:%S")
    timer = time.time() + 60 * 15
    with open('btc_changes.txt', 'r') as f:
        data = f.readlines()
    if not data:
        with open('btc_changes.txt', 'w') as f:
            f.write(f"{timer}\n{date_time}\n{currentprice}")
    with open('btc_changes.txt', 'r') as f:
        data = f.readlines()
    if (decimal.Decimal(data[0]) < time.time()):
        with open('btc_changes.txt', 'w') as f:
            f.write(f"{timer}\n{date_time}\n{currentprice}")
    if float(data[2]) < price_low  or float(data[2]) > price_high:
        print('BTC is sterk veranderd in 15 minuten, tijd om te slapen.')
        time.sleep(1200)
    function_count()


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

function_checkbtc()

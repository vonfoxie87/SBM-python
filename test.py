from binance.client import Client
import talib as ta
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.io as pio
import plotly.graph_objects as go
import decimal


def function_count():
    symbol = 'ETHBTC'
    starttime = '1 day ago UTC'  # to start for 1 day ago
    interval_num = 3
    interval_let = "m"
    interval = str(interval_num) + interval_let
    # interval = '3m'
    klines = trader.client.get_historical_klines(symbol, interval, starttime)
    volume = trader.client.get_ticker(symbol=symbol)['quoteVolume']

    ask_price = trader.client.get_orderbook_ticker(symbol=symbol)
    print(ask_price['askPrice'])


    open_time = [int(entry[0]) for entry in klines]
    open = [float(entry[1]) for entry in klines]
    high = [float(entry[2]) for entry in klines]
    low = [float(entry[3]) for entry in klines]
    close = [float(entry[4]) for entry in klines]
    high_array = np.asarray(high)
    low_array = np.asarray(low)
    close_array = np.asarray(close)
    new_time = [datetime.fromtimestamp(time/1000) for time in open_time]

    slowk, slowd = ta.STOCH(high_array, low_array, close_array, fastk_period=14, slowk_period=1, slowk_matype=0, slowd_period=3, slowd_matype=0)
    psar = ta.SAR(high_array, low_array, acceleration=0.02, maximum=0.2)
    ma200 = ta.MA(close_array, 200)
    ma50 = ta.MA(close_array, 50)
    ma20 = ta.MA(close_array, 20)
    st = ta.STDDEV(close_array, timeperiod=20, nbdev=1)

    upper_bb = (ma20[-2] + 2 * st[-2])
    lower_bb = (ma20[-2] - 2 * st[-2])

    print(decimal.Decimal(psar[-1]))
    print(decimal.Decimal(ma20[-1]))

    fig = go.Figure(go.Scatter(x=new_time,
                            y=slowk,
                            line=dict(color='black', width=2)
                            ))
    fig.add_trace(go.Scatter(x=new_time,
                            y=slowd,
                            line=dict(color='blue', width=1)
                            ))
    fig.show()


class Trader:
    def __init__(self, file):
        self.connect(file)

    def connect(self, file):
        lines = [line.rstrip('\n') for line in open(file)]
        key = lines[0]
        secret = lines[1]
        self.client = Client(key, secret)

    def getBalances(self):
        prices = self.client.get_widraw_history()
        return prices


filename = 'credentials.txt'
trader = Trader(filename)

function_count()

from binance.client import Client
import decimal
import time
import decimal


def function_count():
    symbol = 'HOOKBUSD'
    stepsize_client = trader.client.get_symbol_info(symbol)
    stepsize = float(stepsize_client['filters'][0]['tickSize'])
    print(stepsize)
'''
    print(upper_bb)
    print(lower_bb)

    print('psar:')
    print(decimal.Decimal(psar[-1]))
    print('\nMA20:')
    print(decimal.Decimal(ma20[-1]))

    fig = go.Figure(go.Scatter(x=new_time,
                            y=psar,
                            line=dict(color='black', width=2)
                            ))
    fig.add_trace(go.Scatter(x=new_time,
                            y=ma20,
                            line=dict(color='blue', width=1)
                            ))
    fig.show()
'''

def volume():
    symbols = []
    symbols_correct = []
    all_coins = trader.client.get_all_tickers()
    for i in range(len(all_coins)):
        if all_coins[i]['symbol'][-4:] == "BUSD":
            symbols.append(all_coins[i]['symbol'])
    for i in symbols:
        volume = trader.client.get_ticker(symbol=i)['quoteVolume']
        if i[-3:] == 'BTC':
            if decimal.Decimal(volume) > 100:
                symbols_correct.append(i)
        if i[-4:] == 'BUSD':
            if decimal.Decimal(volume) > 5000000:
                symbols_correct.append(i)


def vol_method_two():
    with open('coins_btc.txt', 'r') as f:
         data = f.readlines()
    timer = time.time() + 60 * 60
    if not data:
        with open('coins_btc.txt', 'w') as f:
            f.write(f"{time.time()}\n")
        time.sleep(3)
    with open('coins_btc.txt', 'r') as f:
         data = f.readlines()
    if (decimal.Decimal(data[0]) < time.time()):
        print('start')
        with open('coins_btc.txt', 'w') as f:
            f.write(f"{timer}\n")
        with open('coins_busd.txt', 'w') as f:
            f.write(f"{time.time()}\n")
        get_all = trader.client.get_ticker()
        for i in get_all:
            if decimal.Decimal(i['quoteVolume']) > 100 and i['symbol'][-3:] == 'BTC':
                with open('coins_btc.txt', 'a') as f:
                    f.write(f"{i['symbol']},")
            if decimal.Decimal(i['quoteVolume']) > 5000000 and i['symbol'][-4:] == 'BUSD':
                with open('coins_busd.txt', 'a') as f:
                    f.write(f"{i['symbol']},")


class Trader:
    def __init__(self, file):
        self.connect(file)

    def connect(self, file):
        self.client = Client('5CHxl9jlu6JeaT5PEriemkQk74UnAlNP4iLtHcZmp5HbAbzaFBh8skUIN0vx2IQU', '5KTj3K13YNfvnf3ycEZspDIz2ft1ULTBNCbQceJGAVUfr5TEjUnhgsHYLsK5JnXm')

    def getBalances(self):
        prices = self.client.get_widraw_history()
        return prices


filename = 'credentials.txt'
trader = Trader(filename)

function_count()

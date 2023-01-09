import urllib.request

symbol = "BTCBUSD"
chart_key = "LyovIcTprVaxS5xLnBRad4yWdUBiG6kq6ctemxcy"
chart_url = f"https://api.chart-img.com/v1/tradingview/advanced-chart?interval=1m&symbol=BINANCE:{symbol}&studies=SAR&studies=BB&studies=MACD&studies=MA:50,close&studies=MA:200,close&key={chart_key}"


urllib.request.urlretrieve(chart_url, "chart.jpg")
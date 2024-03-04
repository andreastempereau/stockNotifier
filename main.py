import os
import time
import pandas_datareader as web
from winotify import Notification, audio

tickers = ['APPL', 'AMD', 'NVDA', 'TSLA']

for ticker in tickers:
    print(web.DataReader(ticker, 'yahoo').iloc[-1]['Close'])

upper_limits = [200, 250, 800, 250]
lower_limits = [180, 180, 700, 180]

while True:
    last_prices = [web.DataReader(ticker, "yahoo")["Adj Close"][-1] for ticker in tickers]
    prev_close = [web.DataReader(ticker, "yahoo")["Close"][-2] for ticker in tickers]
    time.sleep(2)
    for i in range(len(tickers)):
        if last_prices[i] > upper_limits[i]:
            price_change = (last_prices[i] - prev_close[i]) / prev_close[i] * 100
            toast = Notification(app_id="Stock Alarm Bot", title="Price Alert for " + tickers[i],
                                 msg=f"{tickers[i]} has reached a price of {last_prices[i]}. (Last price {prev_close[i]}). {price_change[i]}% increase detected. You may want to sell")
            
            toast.show()
        
        elif last_prices[i] < lower_limits[i]:
            price_change = (last_prices[i] - prev_close[i]) / prev_close[i] * 100
            toast = Notification(app_id="Stock Alarm Bot", title="Price Alert for " + tickers[i],
                                 msg=f"{tickers[i]} has reached a price of {last_prices[i]}. (Last price {prev_close[i]}). {price_change[i]}% increase detected. You may want to buy")
            
            toast.show()
        time.sleep(1)

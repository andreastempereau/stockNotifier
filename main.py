import os
import time
import pandas_datareader as web
import pync
import configparser as cg
import sqlite3
import datetime

conn = sqlite3.connect('config.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS historical_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                price REAL NOT NULL,
                datetime TEXT NOT NULL
             )""")

conn.commit()
conn.close()

def fetch_stock_data(ticker):
    try:
        data = web.DataReader(ticker, "yahoo")
        current_price = data["Adj Close"][-1]
        prev_close = data["Close"][-2]

        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO historical_prices (ticker, price, datetime) VALUES (?, ?, ?)", (ticker, current_price, timestamp))
        conn.commit()
        conn.close()
        return data["Adj Close"][-1], data["Close"][-2]
    

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None, None

def get_historical_prices(ticker, limit=10):
    conn = sqlite3.connect('config.db')
    c = conn.cursor()

    c.execute("SELECT price, datetime FROM historical_prices WHERE ticker = ? ORDER BY id DESC LIMIT ?", (ticker, limit))
    historical_data = c.fetchall()

    conn.close()
    return historical_data

def calculate_price_change(current_price, prev_close):
    if prev_close:
        price_change = (current_price - prev_close) / prev_close * 100
        return price_change
    return 0

def send_notification(ticker, current_price, prev_close, price_change, is_buy, is_sell):
    action = "buy" if is_buy else "sell" if is_sell else "hold"
    message = f"{ticker} has reached a price of {current_price:.2f}. (Previous Close: {prev_close:.2f})" \
              f"\n{price_change:.2f}% change detected. You may want to {action}."
    pync.notify(message, title=f"Stock Alert: {ticker}")

def run():
    config = cg.ConfigParser()
    config.read('config.ini')

    tickers = config.get('tickers', 'symbols').split(',')
    upper_limits = [int(x) for x in config.get('limits', 'upper_limits').split(',')]
    lower_limits = [int(x) for x in config.get('limits', 'lower_limits').split(',')]

    for ticker in tickers:
        print(web.DataReader(ticker, 'yahoo').iloc[-1]['Close'])

    while True:
        for i, ticker in enumerate(tickers):
            current_price, prev_close = fetch_stock_data(ticker)
            if current_price is None or prev_close is None:
                continue

            price_change = calculate_price_change(current_price, prev_close)

            is_buy = current_price < lower_limits[i]
            is_sell = current_price > upper_limits[i]

            send_notification(ticker, current_price, prev_close, price_change, is_buy, is_sell)

        time.sleep(60)  # Wait for 1 minute before checking again

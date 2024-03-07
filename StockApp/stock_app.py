from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

import os
import time
import pandas_datareader as web
import pync
import configparser as cg
import sqlite3
import datetime

from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.clock import Clock

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

class StockApp(App):
    stock_list = ObjectProperty(None)
    stock_input = ObjectProperty(None)

    def add_ticker(self, ticker):
        if ticker and ticker not in [stock_box.children[0].text for stock_box in self.stock_list.children]:
            self.add_stock(ticker)

    def build(self):
        self.load_tickers()
        Clock.schedule_interval(self.update_stocks, 60)
        return self.root

    def load_tickers(self):
        config = cg.ConfigParser()
        config.read('config.ini')
        tickers = config.get('tickers', 'symbols').split(',')
        for ticker in tickers:
            self.add_stock(ticker)

    def add_stock(self, ticker):
        stock_box = BoxLayout(size_hint_y=None, height='30sp')
        ticker_label = Label(text=ticker)
        price_label = Label(text='Loading...')
        change_label = Label(text='')
        stock_box.add_widget(ticker_label)
        stock_box.add_widget(price_label)
        stock_box.add_widget(change_label)
        self.stock_list.add_widget(stock_box)

    def update_stocks(self, *args):
        for stock_box in self.stock_list.children:
            ticker = stock_box.children[0].text
            current_price, prev_close = fetch_stock_data(ticker)
            if current_price is not None and prev_close is not None:
                price_change = calculate_price_change(current_price, prev_close)
                stock_box.children[1].text = f'{current_price:.2f}'
                stock_box.children[2].text = f'{price_change:.2f}%'

    def on_stop(self):
        pass

if __name__ == '__main__':
    from kivy.core.window import Window
    Window.clearcolor = (0.2, 0.2, 0.2, 1)  # Set a dark background color
    StockApp().run()
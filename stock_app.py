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
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
print("TESTTTTTT")
print(os.getcwd())
class StockBox(BoxLayout):
    ticker = StringProperty()
    price = StringProperty()
    change = StringProperty()

class StockApp(App):
    stock_list = ObjectProperty(None)
    stock_input = ObjectProperty(None)

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

    def add_ticker(self, ticker):
        if ticker and ticker not in [stock_box.children[0].text for stock_box in self.stock_list.children]:
            self.add_stock(ticker)

    def load_tickers(self):
        tickers = ['APPL', 'AMD', 'NVDA', 'TSLA']
        for ticker in tickers:
            self.add_stock(ticker)

    def add_stock(self, ticker):
        if self.stock_list is not None:
            stock_box = StockBox(ticker=ticker, price='Loading...', change='')
            self.stock_list.add_widget(stock_box)
        else:
            print("stock_list is None")

    def update_stocks(self, *args):
        if self.stock_list is not None:
            for stock_box in self.stock_list.children:
                ticker = stock_box.ticker
                current_price, prev_close = self.fetch_stock_data(ticker)
                if current_price is not None and prev_close is not None:
                    price_change = self.calculate_price_change(current_price, prev_close)
                    stock_box.price = f'{current_price:.2f}'
                    stock_box.change = f'{price_change:.2f}%'
        else:
            print("stock_list is None")

    def build(self):
        current_dir = os.getcwd()
        self.root = Builder.load_file(os.path.join(current_dir, 'stock_app.kv'))
        if self.root:
            self.stock_list = self.root.ids.stock_list
            self.stock_input = self.root.ids.stock_input
        else:
            print("Failed to load Kivy file")
        self.load_tickers()
        return self.root
    
    def on_stop(self):
        pass

if __name__ == '__main__':
    from kivy.core.window import Window
    Window.clearcolor = (0.2, 0.2, 0.2, 1)  # Set a dark background color
    StockApp().run()
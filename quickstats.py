#!/usr/bin/env python3

import pandas as pd
from twelvedata import TDClient
from matplotlib import pyplot as plt
from datetime import datetime

class Split:
    def __init__(self, ratio, date):
        self.ratio = ratio
        self.date = date
    
    def __str__(self):
        return f"""
        ===== Split =====
        Ratio: {self.ratio}
        Date: {self.date}
        ================="""
    
    def __repr__(self):
        return f'Split(ratio={self.ratio}, date={self.date})'


class Trade:
    def __init__(self, quantity, price, trade_type, date, currency):
        self.quantity = quantity
        self.price = price
        self.trade_type = trade_type
        self.date = date
        self.currency = currency

    def __str__(self):
        return f"""
        ===== Trade =====
        Type: {self.trade_type}
        Quantity: {self.quantity}
        Price: {self.price}
        Date: {self.date}
        Currency: {self.currency}
        ================="""
    
    def __repr__(self):
        return f'Trade(quantity={self.quantity}, price={self.price}, type={self.trade_type}, date={self.date}, currency={self.currency})'


class Ticker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.event_log = None
        self.current_price = 1

    def add_event(self, new_event):
        if self.event_log is None:
            assert not isinstance(new_event, Split), f"First trade for ticker={self.ticker} can NOT be type=Split"
            self.event_log = [new_event]
        else:
            # Insert trades in date order
            # Splits will always be put last -> their date is after market close so after trades that day
            for i, logged_event in enumerate(self.event_log):
                if (new_event.date < logged_event.date) or (new_event.date == logged_event.date and isinstance(logged_event, Split) and isinstance(new_event, Trade)):
                    self.event_log.insert(i, new_event)
                    return
            self.event_log.append(new_event)

    
    def quantity_held(self):
        total = 0
        for event in self.event_log:
            if not isinstance(event, Split) and event.trade_type == "BUY": 
                total += event.quantity
            elif isinstance(event, Split): total *= event.ratio
            else:
                raise TypeError(f"Unrecognised trade of type {type(event)} from {event}")
        return total
        
    def ammount_invested(self):
        total = 0
        for trade in self.event_log:
            if not isinstance(trade, Split) and trade.trade_type == "BUY": total += (trade.quantity * trade.price)
        return total

    def total_value(self):
        assert self.current_price is not None, "must call get_latest_price from Dashboard first"
        return self.quantity_held() * self.current_price

    def profit(self):
        return self.total_value() - self.ammount_invested()
    
    def avg_price_per_share(self):
        return self.ammount_invested() / self.quantity_held()
    
    def __repr__(self):
        return f'Ticker({self.ticker}): {len(self.event_log)} events, {self.quantity_held()} current shares'
    
    def __str__(self):
        delim = '\n'
        print('event log:', self.event_log)
        return f"""
        ===== {self.ticker} =====
        {delim.join([event.__repr__() for event in self.event_log])}
        ================"""



class Dashboard:
    def __init__(self):
        self.tickers = {}
        self.td = TDClient(apikey=open('API_key.txt', 'r').read().strip())
        self.default_currency = 'AUD'
    
    def from_df(self, df):
        exchange_rate_cache = {self.default_currency: 1, 'USD':0.6}
        for i in range(len(df)):
            event = df.loc[i]
            event_date = datetime.strptime(event['Date'], '%d/%m/%y')
            event_quantity = float(event['quantity'])
                
            if event['Currency'] not in exchange_rate_cache:
                print(f'retrieving: {self.default_currency}/{event["Currency"]}')
                exchange_rate_cache[event['Currency']] = self.td.exchange_rate(symbol=f'{self.default_currency}/{event["Currency"]}').as_json()['rate']
            event_price = float(event['share_price']) * exchange_rate_cache[event['Currency']]

            if event['ticker'] not in self.tickers:
                print('creating ticker:', event['ticker'])
                self.add_ticker(Ticker(event['ticker']))

            if event['Type'] == 'BUY' or event['Type'] == 'SELL':
                print('creating trade')
                new_trade = Trade(
                    quantity=event_quantity,
                    price=event_price, 
                    trade_type=event['Type'], 
                    date=event_date, 
                    currency=self.default_currency)
                print('adding trade')
                self.tickers[event['ticker']].add_event(new_trade)
            elif event['Type'] == 'SPLIT':
                print('creating and adding split')
                self.tickers[event['ticker']].add_event(
                    Split(
                        ratio=event_quantity,
                        date=event_date))
            else:
                ValueError("not sure how we're getting here ? #####")

    
    def add_ticker(self, tick):
        self.tickers[tick.ticker] = tick

    def set_default_currency(self, currency):
        self.default_currency = currency
    
    def get_latest_price(self):
        for ticker in self.tickers:
            print(f'getting latest price for |{ticker}|')
            p = self.td.price(symbol=ticker).as_json()
            self.tickers[ticker].current_price = float(p['price'])
    
    def historical(self, start, stop, interval):
        data = self.td.time_series(
            symbol=','.join([ticker for ticker in self.tickers]), 
            start_date=start, 
            end_date=end, 
            interval=interval).as_json()
        plt.plot(data)
    
    def stats(self, currency=None):
        rate = 1
        if currency is not None and currency is not self.default_currency:
            rate = self.td.exchange_rate(symbol=f"{self.default_currency}/{currency}").as_json()['rate']

        cols = ['Ticker', 'NetVal', 'Profit', 'x Mult']
        divider = '-' * 40

        print(f"{'-'*14} Quickstats {'-'*14}")
        print(f"|".join([f'{col:^10}' for col in cols]))
        print(divider)
        for ticker in self.tickers:
            print(f'{ticker:10} {self.tickers[ticker].total_value()*rate:10f} {self.tickers[ticker].profit()*rate:10.2f}')
            print(divider)
    
    def render(self):
        pass
        # TODO: GUI
        # call it show()? 
            
    def __repr__(self):
        return f'Dashboard(): {len(self.tickers)} tickers'
    
    def __str__(self):
        return f"""
        ===== Dashboard =====
        {self.tickers[ticker] for ticker in self.tickers.keys()}
        ====================="""
    
    


if __name__ == "__main__":
    db = Dashboard()
    df = pd.read_csv('sharedata.csv')
    db.from_df(df)
    #db.get_latest_price()
    print(db.stats())




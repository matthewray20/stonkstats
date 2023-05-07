#!/usr/bin/env python3

import pandas as pd
import yaml
from matplotlib import pyplot as plt
from datetime import datetime


# TODO: add cash position
# TODO: implement deposists and selling

class Split:
    def __init__(self, ratio, date):
        self.ratio = ratio
        self.date = date
    
    def __repr__(self):
        return f'Split(ratio={self.ratio}, date={self.date})'


class Trade:
    def __init__(self, quantity, price, date, currency, trade_type):
        self.quantity = quantity
        self.price = price
        self.date = date
        self.currency = currency
        self.trade_type = trade_type
    
    def __repr__(self):
        return f'{self.trade_type}(quantity={self.quantity}, price={self.price}, date={self.date}, currency={self.currency})'


class Cash:
    def __init__(self, quantity, date, currency, trade_type):
        self.quantity = quantity
        self.date = date
        self.currency = currency
        self.cash_type = trade_type
    
    def __repr__(self):
        return f'{self.trade_type}(quantity={self.quantity}, date={self.date}, currency={self.currency})'


class Asset:
    def __init__(self, ticker, asset_type):
        self.ticker = ticker
        self.asset_type = asset_type
        self.asset_api_currency = None
        self.event_log = None
        self.current_price = None

    def add_event(self, new_event):
        if self.event_log is None:
            assert not isinstance(new_event, Split), f"First trade for ticker={self.ticker} can not be type=Split"
            self.event_log = [new_event]
        else:
            # Splits will always be put last -> their date is after market close so after trades that day
            for i, logged_event in enumerate(self.event_log):
                if (new_event.date < logged_event.date) or (new_event.date == logged_event.date and isinstance(logged_event, Split) and isinstance(new_event, Trade)):
                    self.event_log.insert(i, new_event)
                    return
            self.event_log.append(new_event)

    def quantity_held(self):
        total = 0
        for event in self.event_log:
            if isinstance(event, Trade) and event.trade_type == 'buy': total += event.quantity
            elif isinstance(event, Trade) and event.trade_type == 'sell': total -= event.quantity
            elif isinstance(event, Split): total *= event.ratio
            elif isinstance(event, Cash) and event.cash_type == 'deposit': total += event.quantity
            elif isinstance(event, Cash) and event.cash_type == 'withdrawl': total -= event.quantity
            else: raise TypeError(f"Unrecognised trade of type {type(event)} from {event.__repr__()}")
        return total
        
    def ammount_invested(self):
        total = 0
        for trade in self.event_log:
            if isinstance(trade, Trade) and trade.trade_type == 'buy': total += (trade.quantity * trade.price) # + trade.commision
        return total
    
    def is_crypto(self):
        return self.asset_type == 'crypto'
    
    def __repr__(self):
        return f'Asset({self.ticker}): {len(self.event_log)} events, {self.quantity_held()} current shares'


class Portfolio:
    def __init__(self, api, default_currency='AUD'):
        self.assets = {}
        self.default_currency = default_currency
        self.api = api

    def add_asset(self, new_asset):
        self.assets[new_asset.ticker] = new_asset
    
    def get_latest_prices(self, desired_currency):
        for ticker in self.assets:
            print(f'getting latest price for <{ticker}>')
            self.assets[ticker].current_price = self.api.get_latest_price(self.assets[ticker], desired_currency)
    
    def plot_historical(self, start, stop, interval, relative=True):
        # supported intervals are 
        #all_data = {}
        for asset in self.assets:
            dates, prices = self.api.get_historical_prices(asset.ticker, start, stop, interval)
            if relative: 
                initial_price = prices[0]
                prices = [price / initial_price for price in prices]
            #all_data[asset.ticker] = data
            plt.plot(dates, prices, legend=asset.ticker)
        plt.show()
    
    def show_data(self, data, title):
        # find max length
        max_length = 0
        for key, values in data:
            key_len = len_key
            if key_len > max_length: max_length = key_len
            for a_value in values:
                value_len = len(str(a_value))
                if value_len > max_length: max_length = value_len
        
        # parameterised strings for printing as a table
        cols = ['Ticker', 'Quantity', 'Avg Price', 'Invested', 'Cur Value', 'Profit', 'x Mult']
        title_padding = (max_length * len(cols) + len(cols) - 1)//2 - (len(title) + 2 )//2
        divider = '-' * ((max_length + 1) * len(cols) - 1) + '\n'
        
        display_string = f"{'-' * title_padding} {title} {'-' * (title_padding + 1)}\n"
        display_string += f"|".join([f'{col:^{max_length}}' for col in cols]) + '\n'
        display_string += divider
        # print here
        display_string += f'{"Total":>{col_width}}|{"n/a":>{col_width}}|{"n/a":>{col_width}}|{total_invested:{col_width}.2f}|{total_net_value:{col_width}.2f}|{total_net_profit:{col_width}.2f}|{total_xmult:{col_width}.2f}\n'
        display_string += divider
        

        display_string += f'({currency})'
        print(display_string)


    def from_csv(self, filename):
        df = pd.read_csv(filename)
        # ensure data in in the type we expect
        assert set(df.columns) == set(CONFIG["data"]["headers"]), f'{CONFIG["data"]["filepath"]} headers {df.columns} expected to be {CONFIG["data"]["headers"]}'
        assert set(df['eventType']).issubset(set(CONFIG['data']['events'])), 'Error: unexpected eventType in data'
        
        for _, event in df.iterrows():
            # get data of event
            ticker = event['ticker'].to_upper()
            date = datetime.strptime(event['date'], CONFIG['dataConversions']['dateFormat'])
            quantity = float(event['quantity'])
            currency = event['currency'].to_upper()
            event_type = event['eventType'].to_lower()
            price = float(event['price']) * self.api.which_rate(currency, self.default_currency) # (1 if currency == self.default_currency else self.api.get_exchange_rate(currency, self.default_currency))
                                          # self.api.rate(currency, default_currency) -> returns 1 if equal, returns exchange rate if not
            # add new asset if needed
            if ticker not in self.assets:
                new_asset = Asset(ticker, event['assetType'])
                new_asset.asset_api_currency = self.default_currency if new_asset.is_crypto() else self.api.get_currency_info(new_asset.ticker)
                self.add_asset(new_asset)
            
            # add different events
            if event_type == 'buy' or event_type == 'sell':
                self.assets[ticker].add_event(
                    Trade(
                        quantity=quantity,
                        price=price, 
                        trade_type=event_type, 
                        date=date, 
                        currency=self.default_currency))
            elif event_type == 'split':
                self.assets[ticker].add_event(
                    Split(
                        ratio=quantity,
                        date=date))
            elif event_type == 'deposit' or event_type == 'withdrawl':
                self.assets['ticker'].add_event(
                    Cash(
                        quantity=quantity,
                        date=date,
                        currency=currency,
                        cash_type=event_type))
            #else:
                #ValueError(f'Incorrect event type {type(event['eventType'])}. SHould be one of CONFIG["data"]["events"]')

    def quickstats(self, currency=None):
        # def show(headers, data):
        if currency is None: currency = self.default_currency
        # get latest prices for each asset
        self.get_latest_prices(currency)
        # convert to default currency
        #rate = 1 if currency == self.default_currency else self.api.get_exchange_rate(convert_from=self.default_currency, convert_to=currency)
        rate = self.api.which_rate(currency, self.default_currency)
        total_invested, total_net_value = 0, 0

        data = {}
        # calculating stats
        for ticker in self.assets:
            asset = self.assets[ticker]
            # calculate stats
            num_shares = asset.quantity_held()
            invested = asset.ammount_invested() * rate
            total_invested += invested
            avg_price = invested / num_shares
            net_value = num_shares * asset.current_price
            total_net_value += net_value
            net_profit = net_value - invested
            xmult = net_profit / invested
            
            data[ticker] = [num_shares, avg_price, invested, net_value, net_profit, xmult]
            # printing row in table
            display_string += f'{ticker:{col_width}}|{num_shares:{col_width}.2f}|{avg_price:{col_width}.2f}|{invested:{col_width}.2f}|{net_value:{col_width}.2f}|{net_profit:{col_width}.2f}|{xmult:{col_width}.2f}\n'
            display_string += divider
        
        # add total row
        total_net_profit = total_net_value - total_invested
        total_xmult = total_net_profit / total_invested
        data['Total'] = [None, None, total_invested, total_net_value, total_net_profit, total_xmult]
        

        self.get_historical_prices('2023-03-02', '2023-03-08', '1day')
    
    def show_dashboard(self):
        pass
        # TODO: GUI
            
    def __repr__(self):
        return f'Dashboard(): {len(self.assets)} assets'

def build_api():
    # get api and associted api key
    with open(CONFIG['api']['apiKeysFile']) as f:
        api_keys = yaml.load(f, Loader=yaml.FullLoader)
    
    api_backend = CONFIG['api']['apiBackend']
    if api_backend == 'twelveData': api = MyTwelveDataAPI
    elif api_backend == 'alphaVantage': api = MyAlphaVantageAPI
    elif api_backend == 'finnhub': api = MyFinnhubAPI
    else:
        raise ValueError(f'{api_backend} not recognised as an API backend')
    api_key = api_keys[api_backend]
    return api(api_key)



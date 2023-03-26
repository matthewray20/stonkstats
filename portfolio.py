#!/usr/bin/env python3

import pandas as pd
import yaml
from twelvedata import TDClient
from matplotlib import pyplot as plt
from datetime import datetime
from API_backends.twelve_data import MyTwelveDataAPI
from API_backends.alpha_vantage import MyAlphaVantageAPI

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


class Asset:
    def __init__(self, ticker, asset_type):
        self.ticker = ticker
        self.asset_type = asset_type
        self.event_log = None
        self.current_price = 250 #### to be removed

    def add_event(self, new_event):
        if self.event_log is None:
            assert not isinstance(new_event, Split), f"First trade for ticker={self.ticker} can not be type=Split"
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
            if isinstance(event, Trade) and event.trade_type == BUY_DELIM: total += event.quantity
            elif isinstance(event, Split): total *= event.ratio
            else: raise TypeError(f"Unrecognised trade of type {type(event)} from {event.__repr__()}")
        return total
        
    def ammount_invested(self):
        # TODO: account for selling
        total = 0
        for trade in self.event_log:
            if isinstance(trade, Trade) and trade.trade_type == BUY_DELIM: total += (trade.quantity * trade.price)
        return total
    
    def __repr__(self):
        return f'Asset({self.ticker}): {len(self.event_log)} events, {self.quantity_held()} current shares'


class Portfolio:
    def __init__(self, api, default_currency='AUD'):
        self.assets = {}
        self.default_currency = default_currency
        self.api = api
        self.exchange_rate_cache = {self.default_currency: 1, 'USD':0.6}

    def add_asset(self, new_asset):
        self.assets[new_asset.ticker] = new_asset
    
    def get_latest_prices(self):
        for ticker in self.assets:
            print(f'getting latest price for |{ticker}|')
            self.assets[ticker].current_price = self.api.get_latest_price(ticker, sellf.assets[ticker].asset_type)
    
    def plot_historical(self, start, stop, interval):
        data = self.api.get_historical_prices(start, stop, interval, )
        pass

    def from_df(self, df):
        # Asset_Type,Ticker,Quantity,Share_Price,Date,Type,Currency,Commission
        # go through each event
        for i in range(len(df)):
            # get data of event
            event = df.loc[i]
            ticker = event[TICKER_DELIM]
            asset_type = event[ASSET_TYPE_DELIM]
            date = datetime.strptime(event[DATE_DELIM], DATE_FORMAT)
            quantity = float(event[QUANTITY_DELIM])
            currency = event[CURRENCY_DELIM]
            event_type = event[EVENT_TYPE_DELIM]
            
            # get price in proper default currency
            if currency not in self.exchange_rate_cache:
                print(f'retrieving: {self.default_currency}/{currency}')
                self.exchange_rate_cache[currency] = self.api.get_exchange_rate(convert_from=currency, convert_to=self.default_currency)
            price = float(event[PRICE_DELIM]) * self.exchange_rate_cache[currency]

            # add new asset if needed
            if ticker not in self.assets:
                self.add_asset(Asset(ticker, asset_type))

            # if event is buy or sell
            print('#########')
            print(event_type)
            if event_type == BUY_DELIM or event_type == SELL_DELIM:
                self.assets[ticker].add_event(
                    Trade(
                        quantity=quantity,
                        price=price, 
                        trade_type=event_type, 
                        date=date, 
                        currency=self.default_currency))
            # if event is split
            elif event_type == SPLIT_DELIM:
                self.assets[ticker].add_event(
                    Split(
                        ratio=quantity,
                        date=date))
            else:
                ValueError(f'Incorrect event type {type(event[TYPE_DELIM])}. SHould be one of {BUY_DELIM}, {SELL_DELIM}, {SPLIT_DELIM}')
    
    def quickstats(self, currency=None):
        # get latest prices for each asset
        self.get_latest_prices()
        rate = 1
        # convert to default currency
        if currency is not None and currency is not self.default_currency:
            rate = self.api.get_exchange_rate(convert_from=self.default_currency, convert_to=currency)

        # parameterised strings for printing as a table
        cols = ['Ticker', 'Quantity', 'Avg Price', 'Cur Value', 'Profit', 'x Mult']
        col_width = 12
        title = 'Quickstats'
        title_padding = (col_width * len(cols) + len(cols) - 1)//2 - (len(title) + 2 )//2
        divider = '-' * ((col_width + 1) * len(cols) - 1) + '\n'
        display_string = ''
        
        display_string += f"{'-' * title_padding} {title} {'-' * (title_padding + 1)}\n"
        display_string += f"|".join([f'{col:^{col_width}}' for col in cols]) + '\n'
        display_string += divider

        # calculating stats
        for ticker in self.assets:
            asset = self.assets[ticker]

            num_shares = asset.quantity_held()
            invested = asset.ammount_invested() * rate
            avg_price = invested / num_shares
            net_value = num_shares * asset.current_price
            net_profit = net_value - invested

            # printing row in table
            display_string += f'{ticker:{col_width}}|'
            display_string += f'{num_shares:{col_width}.2f}|'
            display_string += f'{avg_price:{col_width}.2f}|'
            display_string += f'{net_value:{col_width}.2f}|'
            display_string += f'{net_profit:{col_width}.2f}|'
            display_string += f'{net_profit / invested:{col_width}.2f}\n'
            display_string += divider

        display_string += f'({currency})'
        print(display_string)
    
    def show_dashboard(self):
        pass
        # TODO: GUI
            
    def __repr__(self):
        return f'Dashboard(): {len(self.assets)} assets'
    


if __name__ == "__main__":
    # TODO: currency is not consistent i.e. getting latest prices (which currency?)
    with open('config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    # getting deliminators from config
    TICKER_DELIM = config['delims']['ticker']
    PRICE_DELIM = config['delims']['price']
    QUANTITY_DELIM = config['delims']['quantity']
    DATE_DELIM = config['delims']['date']
    EVENT_TYPE_DELIM = config['delims']['eventType']
    CURRENCY_DELIM = config['delims']['currency']
    ASSET_TYPE_DELIM = config['delims']['assetType']
    BUY_DELIM = config['delims']['buy']
    SELL_DELIM = config['delims']['sell']
    SPLIT_DELIM = config['delims']['split']
    
    # getting data conversions
    DATE_FORMAT = config['dataConversions']['dateFormat']
    
    # getting variables from config
    default_currency = config['defaultCurrency']
    
    # getting api details from config
    api_key_file = config['api']['apiKeysFile']
    api_backend = config['api']['apiBackend']

    if api_backend == 'twelveData':
        api = MyTwelveDataAPI
    elif api_backend == 'alphaVantage':
        api = MyAlphaVantageAPI
    else:
        raise ValueError(f'{API_BACKEND} not recognised as an API backend')
    
    p = Portfolio(api(api_key_file), default_currency)
    df = pd.read_csv(config['dataPath'])
    p.from_df(df)
    p.quickstats()

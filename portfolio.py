#!/usr/bin/env python3

import pandas as pd
import yaml
import pickle
from matplotlib import pyplot as plt
from datetime import datetime
from common.asset import Asset
from common.events import Split, Trade
from backends.apis.twelve_data import MyTwelveDataAPI
from backends.apis.alpha_vantage import MyAlphaVantageAPI
from backends.apis.financial_modelling_prep import MyFinancialModellingPrepAPI


class Portfolio:
    def __init__(self):
        self.assets = {}
        self.default_currency = 'AUD'
        self.date_format = None
        self.api = None
    
    def __repr__(self):
        return f'Dashboard(): {len(self.assets)} assets'
    
    def __eq__(self, other):
        checks = [
            self.assets == other.assets,
            self.default_currency == other.default_currency
        ]
        return all(checks)
    
    def set_default_currency(self, currency):
        self.default_currency = currency
    
    def set_data_date_format(self, data_format):
        self.date_format = data_format
    
    def set_backend(self, api_keys_filename, backend):
        # get api and associted api key
        with open(api_keys_filename, 'r') as f:
            api_keys = yaml.load(f, Loader=yaml.FullLoader)
        api_key = api_keys[backend]
        
        if backend == 'twelveData': api = MyTwelveDataAPI
        elif backend == 'alphaVantage': api = MyAlphaVantageAPI
        elif backend == 'financialModellingPrep': api = MyFinancialModellingPrepAPI
        else:
            raise ValueError(f'{backend} not recognised as an API backend')
        self.api = api(api_key)
    
    def setup_from_config(self, config):
        if 'defaultCurrency' in config['dataConversions'].keys(): self.set_default_currency(config['dataConversions']['defaultCurrency'])
        if 'dateFormat' in config['dataConversions'].keys(): self.set_data_date_format(config['dataConversions']['dateFormat'])
        if 'apiBackend' in config['api'].keys() and 'apiKeysFile' in config['api'].keys(): self.set_backend(config['api']['apiKeysFile'], config['api']['apiBackend'])
    
    def num_assets(self):
        return len(self.assets)
    
    def save_as_pickle(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
    
    def add_from_pickle(self, filename):
        with open(filename, 'rb') as f:
            other_portfolio = pickle.load(f)
        self.merge_portfolio(other_portfolio)
    
    def merge_portfolio(self, other):
        assert isinstance(other, Portfolio)
        if self.num_assets() == 0 and other.num_assets() != 0: self.assets = other.assets
        for ticker, asset in other.assets.items():
            if ticker not in self.assets: self.add_existing_asset(asset)
            else: self.assets[ticker].merge_asset(asset)
        
    def add_new_asset(self, ticker, asset_type):
        new_asset = Asset(ticker, asset_type)
        new_asset.set_api_currency(self.default_currency if new_asset.is_crypto() else self.api.get_currency_info(new_asset.ticker))
        self.add_existing_asset(new_asset)

    def add_existing_asset(self, new_asset):
        if new_asset in self.assets.values(): self.assets[an_asset.ticker].merge_asset(new_asset)
        else: self.assets[new_asset.ticker] = new_asset
    
    def remove_asset(self, ticker):
        self.assets.pop(ticker)
    
    def remove_asset_ith_event(self, ticker, i):
        self.assets[ticker].remove_ith_event(i)
    
    def add_asset_event(self, ticker, date, quantity, price, event_type, currency, allow_duplicates=False):
        if event_type == 'buy' or event_type == 'sell':
            new_event = Trade(
                quantity=quantity,
                price=price, 
                trade_type=event_type, 
                date=date, 
                currency=currency)
        elif event_type == 'split':
                new_event = Split(
                    ratio=quantity,
                    date=date)
        else:
            raise ValueError(f'Unrecognised event_type {event_type}. Must be buy/sell/split')
        
        self.assets[ticker].add_event(new_event, allow_duplicates)
    
    def add_from_csv(self, filename):
        df = pd.read_csv(filename)
        for _, event in df.iterrows():
            # get data of event
            ticker = event['ticker'].upper()
            date = datetime.strptime(event['date'], self.date_format)
            quantity = float(event['quantity'])
            currency = event['currency'].upper()
            event_type = event['eventType'].lower()
            price = float(event['price']) * self.api.which_rate(currency, self.default_currency) 
            # add new asset if needed
            if ticker not in self.assets:
                self.add_new_asset(ticker, event['assetType'])
            # add different events
            self.add_asset_event(ticker, date, quantity, price, event_type, self.default_currency)
    
    def get_latest_prices(self, desired_currency):
        for ticker in self.assets:
            self.assets[ticker].current_price = self.api.get_latest_price(self.assets[ticker], desired_currency)
    
    def get_historical_prices(start, stop, interval, relative=True):
        for asset in self.assets:
            dates, prices = self.api.get_historical_prices(asset.ticker, start, stop, interval)
            if relative: 
                initial_price = prices[0]
                prices = [price / initial_price for price in prices]
            self.assets[asset.ticker].historical_prices = (dates, prices)

    def plot_historical(self):
        for asset in self.assets:
            dates, prices = asset.historical_prices
            if dates is None or prices is None: continue
            plt.plot(dates, prices, legend=asset.ticker)
        plt.show()
    
    
    def as_table(self, data, title, max_length=0, footnote=None):
        # find max length for printing
        for key in data:
            key_len = len(key)
            if key_len > max_length: max_length = key_len
        # parameterised strings for table creation 
        cols = data.keys()
        title_padding = (max_length * len(cols) + len(cols) - 1)//2 - (len(title) + 1 )//2
        divider = '-' * ((max_length + 1) * len(cols) - 1) + '\n'
        # creating table header
        display_string = f"{'-' * title_padding} {title} {'-' * (title_padding + 1)}\n"
        display_string += f"|".join([f'{col:^{max_length}}' for col in cols]) + '\n'
        display_string += divider
        # printing row in table
        for key, values in data.items():
            display_string += f'{key:{max_length}}'
            length = len(values)
            for i in range(length): 
                display_string += '|' 
                if item is None: display_string += f'{"n/a":{max_length}}'
                if isinstance(item, int) or isinstance(item, float): display_string += f'{item:{max_length}.2f}'
                elif isinstance(item, str): display_string += f'{item}:>{max_length}'
            display_string += '\n' + divider
        
        if footnote is not None:
            display_string += footnote
        
        return display_string
    
    def quickstats(self, currency=None):
        if currency is None: currency = self.default_currency
        # get latest prices for each asset
        self.get_latest_prices(currency)
        rate = self.api.which_rate(currency, self.default_currency)
        total_invested, total_net_value = 0, 0
        # calculating stats
        data = {}
        for ticker in self.assets:
            asset = self.assets[ticker]
            num_shares = asset.quantity_held()
            if num_shares == 0: continue
            invested = asset.ammount_invested() * rate
            total_invested += invested
            avg_price = invested / num_shares
            net_value = num_shares * asset.current_price
            total_net_value += net_value
            net_profit = net_value - invested
            xmult = net_profit / invested
            data[ticker] = [num_shares, avg_price, invested, net_value, net_profit, xmult]
        # add total row
        total_net_profit = total_net_value - total_invested
        total_xmult = total_net_profit / total_invested
        data['Total'] = [None, None, total_invested, total_net_value, total_net_profit, total_xmult]
        
        footnote = f'{currency}'
        self.as_table(data, 'Quickstats', footnote=footnote, max_length=int(total_net_value)+3)
    
    def show_dashboard(self):
        # TODO: GUI
        raise NotImplementedError()
     


#!/usr/bin/env python3

from backends.apis.default_api import DefaultAPI
from backends.utils.decorators import api_error_handling, cache_exchange_rate
from twelvedata import TDClient
from datetime import datetime

# This uses the TwelveData API
# https://github.com/twelvedata/twelvedata-python

class MyTwelveDataAPI(DefaultAPI):
    def __init__(self, api_key):
        super().__init__()
        self.td = TDClient(apikey=api_key)
        self.max_requests_per_min = 8
        self.allowed_historical_intervals = {'daily': '1day', 'weekly': '1week', 'monthly': '1month'}
        
    def _get_security_latest_price(self, ticker):
        return self.td.price(symbol=ticker).as_json()
    
    def _get_crypto_latest_price(self, ticker, desired_currency):
        return self._get_security_latest_price(f'{ticker}/{desired_currency}')
    
    @api_error_handling
    def get_latest_price(self, asset, desired_currency):
        if asset.is_crypto(): return float(self._get_crypto_latest_price(asset.ticker, desired_currency)['price'])
        price = self._get_security_latest_price(asset.ticker)['price']
        # convert currency if api returns in currency other than desired currency
        return float(price) * self.which_rate(asset.asset_api_currency, desired_currency)
    
    def _get_exchange_rate(self, convert_from, convert_to):
        currency_pair = f'{convert_from}/{convert_to}'
        return self.td.exchange_rate(symbol=currency_pair).as_json()

    @api_error_handling
    @cache_exchange_rate
    def get_exchange_rate(self, convert_from, convert_to):
        return float(self._get_exchange_rate(convert_from, convert_to)['rate'])

    def _get_currency_info(self, ticker):
        return self.td.eod(symbol=ticker).as_json()
        
    @api_error_handling
    def get_currency_info(self, ticker):
        return self._get_currency_info(ticker)['currency']
    
    def _get_security_historical_prices(self, ticker, start_date, end_date, interval):
        return self.td.time_series(symbol=ticker, start_date=start_date, end_date=end_date, interval=interval).as_json()

    def _get_crypto_historical_prices(self, ticker, start_date, end_date, interval):
        return self._get_security_historical_prices(symbol=ticker, start_date=start_date, end_date=end_date, interval=interval)
    
    @api_error_handling
    def get_historical_prices(self, asset, start_date, end_date, desired_currency, interval):
        # accepted intervals
        interval = self.check_interval(interval)
        # make API calls
        if asset.is_crypto(): data = self._get_crypto_historical_prices(f'{asset.ticker}/{desired_currency}', start_date, end_date, interval)
        else: data = self._get_security_historical_prices(asset.ticker, start_date, end_date, interval)
        # parse datetimes and price data
        datetimes = [datetime.strptime(period['datetime'], '%y-%m-%d') for period in data]
        rate = self.which_rate(asset.asset_api_currency, desired_currency)
        prices = [float(period['close']) * rate for period in data]
        return datetimes, prices
        

        
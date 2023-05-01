#!/usr/bin/env python3

from backends.apis.default_api import DefaultAPI
from backends.utils.decorators import api_error_handling, cache_exchange_rate
from twelvedata import TDClient

# This uses the TwelveData API
# https://github.com/twelvedata/twelvedata-python

class MyTwelveDataAPI(DefaultAPI):
    def __init__(self, api_key):
        super().__init__()
        self.td = TDClient(apikey=api_key)
        self.max_requests_per_min = 8
        
    def _get_security_latest_price(self, ticker):
        return self.td.price(symbol=ticker).as_json()
    
    def _get_crypto_latest_price(self, ticker, desired_currency):
        return self._get_security_latest_price(f'{ticker}/{desired_currency}')
    
    @api_error_handling
    def get_latest_price(self, asset, desired_currency):
        if asset.asset_type == 'crypto': return float(self._get_crypto_latest_price(asset.ticker, desired_currency)['price'])
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
    
    def _get_security_historical_prices(self, symbol, start_date, end_date, interval):
        return self.td.time_series(symbol=symbol, start_date=start_date, end_date=end_date, interval=interval).as_json()

    def _get_crypto_historical_prices(self, symbol, start_date, end_date, interval):
        return self._get_security_historical_prices(symbol, start_date, end_date, interval)
    
    @api_error_handling
    def get_historical_prices(self, asset, start_date, end_date, desired_currency, interval='1d', relative=True):
        if asset.asset_type == 'crypto': data = self._get_crypto_historical_prices(f'{asset.ticker}/{desired_currency}', start_date, end_date, interval)
        else: data = self._get_security_historical_prices(asset.ticker, start_date, end_date, interval)
        datetimes = [period['datetime'] for period in data]
        if relative:
            initial_price = data[0]['close']
            prices = [float(period['close']) / initial_data for period in data]
        else:
            rate = self.which_rate(asset.asset_api_currency, desired_currency)
            prices = [float(period['close']) * rate for period in data]
        return (datetimes, prices)
        

        
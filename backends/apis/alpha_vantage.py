 #!/usr/bin/env python3

from backends.apis.default_api import DefaultAPI
from backends.utils.decorators import api_error_handling, cache_exchange_rate
import requests
import json
from datetime import datetime

# This uses the alphavantage API
# https://www.alphavantage.co/documentation/

class MyAlphaVantageAPI(DefaultAPI):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.max_requests_per_min = 5
        self.allowed_historical_intervals = {'daily': 'DAILY', 'weekly': 'WEEKLY', 'monthly': 'MONTHLY'}
        self.base_url = 'https://www.alphavantage.co/query?'
        self.api_string = f'&apikey={self.api_key}'
        self.max_requests_per_min = 10
        
    def _get_security_latest_price(self, ticker):
        return requests.get(self.base_url + f'function=GLOBAL_QUOTE&symbol={ticker}' + self.api_string)
    
    def _get_crypto_latest_price(self, ticker, desired_currency):
        return self.get_exchange_rate(ticker, desired_currency)
    
    #@api_error_handling
    def get_latest_price(self, asset, desired_currency):
        # have to access crypto resp in here
        if asset.is_crypto(): return self._get_crypto_latest_price(asset.ticker, desired_currency)
        price_resp = self._get_security_latest_price(asset.ticker)
        price_json = json.loads(price_resp.text)
        price = float(price_json['Global Quote']['05. price'])
        return price * self.which_rate(asset.asset_api_currency, desired_currency)

    def _get_exchange_rate(self, convert_from, convert_to):
        return requests.get(self.base_url + f'function=CURRENCY_EXCHANGE_RATE&from_currency={convert_from}&to_currency={convert_to}' + self.api_string)

    #@api_error_handling
    @cache_exchange_rate
    def get_exchange_rate(self, convert_from, convert_to):
        exchange_rate_resp = self._get_exchange_rate(convert_from, convert_to)
        exchange_rate_json = json.loads(exchange_rate_resp.text)
        exchange_rate = float(exchange_rate_json['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        return exchange_rate
    
    def _get_security_historical_prices(self, ticker, interval):
        return requests.get(self.base_url + f'function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}' + self.api_string)

    def _get_crypto_historical_prices(self, ticker, interval):
        return requests.get(self.base_url + f'function=FX_DAILY&symbol={ticker}' + self.api_string)
    
    #@api_error_handling
    def get_historical_prices(self, asset, start_date, end_date, desired_currency, interval):
        interval = self.check_interval(interval)
        # TODO: if start end dates provided, use outputsize=full to get all data, then parse to dates provided - not sure for crypto
        if asset.is_crypto():
            resp = self._get_crypto_historical_prices(asset.ticker, interval)
            key = f'4a. close ({desired_currency})'
            func = 'Time Series (Digital Currency Daily)' # Daily only for daily endpoint
        else:
            resp = self._get_security_historical_prices(asset.ticker, interval)
            key = '4. close'
            func = 'Time Series (Daily)'
        data = json.loads(resp.text)
        data = data[func][func]
        dates = list(data.keys())
        datetimes = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
        rate = self.which_rate(asset.asset_api_currency, desired_currency)
        prices = [float(data[datetimes[i]][key]) * rate for i in range(len(data))]
        return datetimes, prices
        

    def _get_currency_info(self, ticker):
        return requests.get(self.base_url + f'function=OVERVIEW&symbol={ticker}' + self.api_string)
    
    #@api_error_handling
    def get_currency_info(self, ticker):
        resp = self._get_currency_info(ticker)
        data = json.loads(resp.text)
        return data['Currency']

    
    
    
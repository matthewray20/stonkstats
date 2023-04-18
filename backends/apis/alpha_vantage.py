 #!/usr/bin/env python3

from backends.apis.default_api import DefaultAPI
from backends.utils.decorators import api_error_handling, cache_exchange_rate
import requests
import json

# This uses the alphavantage API
# https://www.alphavantage.co/documentation/

class MyAlphaVantageAPI(DefaultAPI):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.max_requests_per_min = 5
        self.base_url = 'https://www.alphavantage.co/query?'
        self.api_string = f'&apikey={self.api_key}'
        self.max_requests_per_min = 0
        
    def _get_security_latest_price(self, ticker):
        return requests.get(self.base_url + f'function=GLOBAL_QUOTE&symbol={ticker}' + self.api_string)
    
    def _get_crypto_latest_price(self, ticker, desired_currency):
        return self.get_exchange_rate(ticker, desired_currency)
    
    @api_error_handling
    def get_latest_price(self, asset, desired_currency):
        if asset.asset_type == 'crypto': return self_get_crypto_latest_price(asset.ticker, desired_currency)
        price_resp = self._get_latest_price(asset.ticker)
        price_json = json.loads(price_resp.text)
        price = float(price_json['Global Quote']['05. price'])
        return price * self.which_rate(asset.asset_api_currency, desired_currency)

    def _get_exchange_rate(self, convert_from, convert_to):
        return requests.get(self.base_url + f'function=CURRENCY_EXCHANGE_RATE&from_currency={convert_from}&to_currency={convert_to}' + self.api_string)

    @api_error_handling
    @cache_exchange_rate
    def get_exchange_rate(self, convert_from, convert_to):
        exchange_rate_resp = self._get_exchange_rate(convert_from, convert_to)
        # get exchange rate and return it
        exchange_rate_json = json.loads(resp.text)
        exchange_rate = float(exchange_rate_json['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        return exchange_rate
    
    def _get_historical_prices(self):
        pass

    @api_error_handling
    def get_historical_prices(self, start_date, end_date, interval='1d', *args):
        return 0
    
    def _get_currency_info(self, ticker):
        pass
    
    @api_error_handling
    def get_currency_info(self, ticker):
        pass
    
    
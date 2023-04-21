#!/usr/bin/env python3

from API_backends.default_api import DefaultAPI
from backends.utils.decorators import api_error_handling, cache_exchange_rate
import requests
import json

class MyTiingoAPI:
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.base_url = 'https://api.tiingo.com/tiingo/'
        self.headers = {'Content-Type': 'application/json'}
        self.api_string = f'?token={self.api_key}'
        
    def _get_security_latest_price(self, ticker):
        return requests.get(self.base_url + f'daily/{asset.ticker}/prices' + self.api_string, headers=self.headers)
    
    def _get_crypto_latest_price(self, ticker, desired_currency):
        return requests.get(self.base_url + f'crypto/prices?tickers={asset.ticker}{desired_currency}' + self.api_string, headers=self.headers)

    @api_error_handling
    def get_latest_price(self, asset, desired_currency):
        if asset.asset_type == 'crypto': return self._get_crypto_latest_price(asset.ticker, desired_currency)
        # get price and error check
        price_resp = self._get_security_latest_price(ticker)
        price_json = json.loads(resp.text)
        price = float(price_json[0]['adjClose'])
        return price * self.which_rate(asset.asset_api_currency, desired_currency)

    def _get_exchange_rate(self, convert_from, convert_to):
        pass
    
    @api_error_handling
    @cache_exchange_rate
    def get_exchange_rate(self, convert_from, convert_to):
        pass

    def _get_currency_info(self, asset):
        pass
    
    @api_error_handling
    def get_currency_info(self, asset):
        resp = requests.get(self.base_url + f'fundamentals/{asset.ticker}' + self.api_string, headers=self.headers)
        return json.loads(resp.text)
    
    def _get_historical_prices(self):
        pass
    
    @api_error_handling
    def get_historical_prices(self, start_date, end_date, *args):
        rpass

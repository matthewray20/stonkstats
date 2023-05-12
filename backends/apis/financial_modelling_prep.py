#!/usr/bin/env python3

from backends.apis.default_api import DefaultAPI
from backends.utils.decorators import api_error_handling, cache_exchange_rate
import requests
import json
from datetime import datetime

# This uses the TwelveData API
# https://site.financialmodelingprep.com/developer/docs/

class MyFinancialModellingPrepAPI(DefaultAPI):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.max_requests_per_min = 250
        self.allowed_historical_intervals = {'daily': 'daily'}
        self.base_url = 'https://financialmodelingprep.com/'
        self.api_string = f'?apikey={self.api_key}'
    
    def _get_security_latest_price(self, ticker):
        return requests.get(self.base_url + f'api/v3/quote-short/{ticker}' + self.api_string)
    
    def _get_crypto_latest_price(self, ticker):
        return requests.get(self.base_url + f'api/v3/quote/{ticker}USD' + self.api_string)

    #@api_error_handling
    def get_latest_price(self, asset, desired_currency):
        if asset.is_crypto():
            resp = self._get_crypto_latest_price(asset.ticker)
            rate = 1 if desired_currency == 'USD' else self.get_exchange_rate('USD', desired_currency)
        else:
            resp = self._get_security_latest_price(asset.ticker)
            rate = 1 if asset.asset_api_currency == desired_currency else self.get_exchange_rate(asset.asset_api_currency, desired_currency)
        data = json.loads(resp.text)
        return float(data[0]['price']) * rate

    def _get_security_historical_prices(self, ticker, start_date, end_date, interval):
        return requests.get(self.base_url + f'api/v3/historical-price-full/{ticker}?from={start_date}&to={end_date}&apikey={aself.pi_key}')
    
    def _get_crypto_historical_prices(self, ticker, start_date, end_date, interval):
        return requests.get(self.base_url + f'api/v3/historical-price-full/{ticker}USD?from={start_date}&to={end_date}&apikey={api_key}')

    #@api_error_handling
    def get_historical_prices(self, asset, start_date, end_date, desired_currency, interval):
        interval = self.check_interval(interval)
        if asset.is_crypto(): 
            resp = self._get_crypto_historical_prices(ticker, start_date, end_date, interval)
            rate = 1 if desired_currency == 'USD' else self.get_exchange_rate('USD', desired_currency)
        else:
            resp = self._get_security_historical_prices(ticker, start_date, end_date, interval)
            rate = 1 if asset.asset_api_currency == desired_currency else self.get_exchange_rate(asset.asset_api_currency, desired_currency)
        data = json.loads(resp.text)
        datetimes = [datetime.strptime(period['date'], '%Y-%m-%d') for period in data['historical']]
        prices = [float(period['close']) * rate for period in data['historical']]
        return datetimes, prices


    def _get_exchange_rate(self, currency):
        return requests.get(self.base_url + f'api/v3/fx/{currency}USD' + self.api_string)    

    #@api_error_handling
    @cache_exchange_rate
    def get_exchange_rate(self, convert_from, convert_to):
        if convert_to == 'USD': 
            resp = self._get_exchange_rate(convert_from)
            data = json.loads(resp.text)
            return float(data[0]['bid'])
        elif convert_from == 'USD': 
            resp = self._get_exchange_rate(convert_to)
            data = json.loads(resp.text)
            return 1 / float(data[0]['bid'])
        else:
            resp_conevrt_from_to_usd = self._get_exchange_rate(convert_from)
            data_convert_from = json.loads(resp_conevrt_from_to_usd.text)
            resp_usd_to_convert_to = self._get_exchange_rate(convert_to)
            data_convert_to = json.loads(resp_usd_to_convert_to.text)
            return  float(data_convert_from[0]['bid']) * (1 / float(data_convert_to[0]['bid']))

    def _get_currency_info(self, ticker):
        return requests.get(self.base_url + f'api/v3/profile/{ticker}' + self.api_string)

    #@api_error_handling
    def get_currency_info(self, ticker):
        resp = self._get_currency_info(ticker)
        data = json.loads(resp.text)
        return data[0]['currency'].upper()
    

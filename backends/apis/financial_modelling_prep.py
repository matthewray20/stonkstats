#!/usr/bin/env python3

from backends.apis.default_api import DefaultAPI
from backends.utils.decorators import api_error_handling, cache_exchange_rate
import requests
import json

# This uses the TwelveData API
# https://site.financialmodelingprep.com/developer/docs/

class MyFinancialModellingPrepAPI(DefaultAPI):
    def __init__(self):
        super().__init__()
        self.api_key = api_key
        self.max_requests_per_min = 250
    
    def _get_security_latest_price(self, ticker):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented _get_security_latest_price()')
    
    def _get_crypto_latest_price(self, ticker, desired_currency):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented _get_crypto_latest_price()')

    def get_latest_price(self, asset, desired_currency):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_latest_price()')

    def _get_security_historical_prices(self, start_date, end_date, *args):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented _get_security_historical_prices()')
    
    def _get_crypto_historical_prices(self, start_date, end_date, *args):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented _get_crypto_historical_prices()')
    
    def get_historical_prices(self, start_date, end_date, *args):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_historical_prices()')
    
    def _get_exchange_rate(self, convert_from, convert_to):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented _get_exchange_rate()')
    
    def get_exchange_rate(self, convert_from, convert_to):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_exchange_rate()')

    def _get_currency_info(self, asset):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented _get_currency_info()')
    
    def get_currency_info(self, asset):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_currency_info()')
    
#!/usr/bin/env python3

class DefaultAPI:
    def __init__(self):
        self.exchange_rate_cache = {}
        self.allowed_historical_intervals = {}
    
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
    
    def which_rate(self, asset_currency, desired_currency):
        return 1 if asset_currency == desired_currency else self.get_exchange_rate(asset_currency, desired_currency)
    
    def check_interval(self, interval):
        if interval not in self.allowed_historical_intervals:
            print(f'interval {interval} not accepted be {self.__name__} backend. Using interval=daily')
            return self.allowed_historical_intervals['daily']
        else:
            return self.allowed_historical_intervals[interval]
    
    @staticmethod
    def _api_error_message(endpoint, *args):
        messages = {
            'get_latest_price': 'Error getting latest price',
            'get_exchange_rate': f'Error getting exchange rate from {args[0]} to {args[1]}',
            'get_historical_prices': 'Error getting historical prices',
            'get_currency_info': 'Error getting currency info'
        }
        return messages[endpoint] if endpoint in messages else 'Unknown Error'
    
    



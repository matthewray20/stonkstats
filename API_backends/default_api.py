#!/usr/bin/env python3

class DefaultAPI:
    def __init__(self):
        self.exchange_rate_cache = {}

    def get_latest_price(self, asset, desired_currency):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_latest_price()')
    
    def get_exchange_rate(self, convert_from, convert_to):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_exchange_rate()')
    
    def get_historical_prices(self, start_date, end_date, *args):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_hsitorical_prices()')
    
    # TODO: handle errors better
    # not quite writing per method per API class, but not much better
    # could i wrap something and provide it that way???
    # PROBLEM: each api will have different ways of reporting errors. How to handle for this?
    @staticmethod
    def print_error_message(action, *args):
        if action == 'exchange_rate':
            assert len(args) == 2, 'Should provide args <from> and <to> for exchange rate'
            print(f'ERROR getting exchange rate from {args[0]} -> {args[1]}')
        elif action == 'price':
            assert len(args) == 1, 'Should provide arg <ticker> for prices'
            print(f'ERROR getting price for {args[0]}')
        elif action == 'currency_info':
            assert len(args) == 1, 'Should provide arg <ticker> for currency info'
            print(f'ERROR getting currency info for {args[0]}')
        elif action == 'historical':
            print(f'ERROR getting historical data')
        return


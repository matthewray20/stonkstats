#!/usr/bin/env python3

import time

def api_error_handling(func):
    def api_error_handling_wrapper(self, *args, **kwargs):
        # avoid rate limits
        sleep_time = 60 // self.max_requests_per_min + 1
        time.sleep(sleep_time)
        # call func and general error handling
        # doesnt need details about error as will have tests for that
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            print(self._api_error_message(func.__name__))
            print(e)
            return None
    return api_error_handling_wrapper



def cache_exchange_rate(func):
    def cache_exchange_rate_wrapper(self, convert_from, convert_to):
        currency_pair = f'{convert_from}/{convert_to}'
        # check if currency pair in cache - if True return it
        if currency_pair in self.exchange_rate_cache: return self.exchange_rate_cache[currency_pair]
        # get exchange rate
        exchange_rate = func(convert_from, convert_to)
        # cache exchange rate
        self.exchange_rate_cache[currency_pair] = exchange_rate
        return exchange_rate
    return cache_exchange_rate_wrapper

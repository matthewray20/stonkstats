#!/usr/bin/env python3

import functools
import time

# This is a general error handling decorator for the backend api calls
# Not designed to be specific
def api_error_handling(func):
    functools.wraps(func)
    def api_error_handling_wrapper(self, *args, **kwargs):
        # avoid rate limits
        sleep_time = 60 // self.max_requests_per_min + 1
        #print(func.__name__, 'sleeping for:', sleep_time, 'seconds')
        time.sleep(sleep_time)
        # call func and general error handling
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            #print(self._api_error_message(func.__name__))
            print(e)
            return None
    return api_error_handling_wrapper

# This is a layer on top of the get_exchange_rate API method to catch 
# incoming calls and return the exchange rate if it is in the cache, if not
# in the cache, make api call and cache result before retuning it
def cache_exchange_rate(func):
    functools.wraps(func)
    def cache_exchange_rate_wrapper(self, convert_from, convert_to):
        currency_pair = f'{convert_from}/{convert_to}'
        alternate_pair = f'{convert_to}/{convert_from}'
        # check if currency pair in cache - if True return it
        if currency_pair in self.exchange_rate_cache: return self.exchange_rate_cache[currency_pair]
        elif alternate_pair in self.exchange_rate_cache: return 1 / self.exchange_rate_cache[alternate_pair]
        # get exchange rate
        exchange_rate = func(self, convert_from, convert_to)
        # cache exchange rate
        self.exchange_rate_cache[currency_pair] = exchange_rate
        return exchange_rate
    return cache_exchange_rate_wrapper

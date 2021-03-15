from __future__ import annotations
from pprint import pprint

import random
import time
from dataclasses import dataclass
from enum import Enum
from http import HTTPStatus
from typing import List
from typing import Mapping

import requests

class Currency(Enum):
   EUR = 'EUR'
   GBP = 'GBP'
   USD = 'USD'

@dataclass
class ExchangeRate:
    base: Currency
    rates: Mapping[str, float]

class CurrencyCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.currency_priority = set()
        self.current_currency_rates = {}
        
    def get(self, baseCurrency: Currency):
        self.current_currency_rates.get(baseCurrency, None)
        
    def put(self, rate: ExchangeRate):

        print(f'Putting {rate.base} into cache')
        if len(self.currency_priority) > self.capacity:
            popped_currency = self.currency_priority.pop().base
            del self.current_currency_rates[popped_currency]
            
            print("Currency cache exceeds capacity of: {} removing: {} from cache"
                  .format(self.capacity, popped_currency))
        
        currency = rate.base
        

        print("Adding currency: {} too list".format(currency))
        self.current_currency_rates[currency] = rate
        self.currency_priority.add(currency)

class ExchangeRateApiClient:
    
    def __init__(self):
        self.currency_cache = CurrencyCache(2)
        
    def get_latest_rate(self, base_currency: Currency) -> ExchangeRate:
        print(f'Getting rates for {base_currency}')
        in_currency_cache = self.currency_cache.get(base_currency)
        if in_currency_cache is not None:
            return in_currency_cache
        else:
            print(f'Exchange rate API called for base currency {base_currency}')
            params = {'base': base_currency.value}
            response = requests.get('https://api.exchangeratesapi.io/latest', params)
            if response.status_code != HTTPStatus.OK:
                raise Exception(f'Error while getting rates for currency {base_currency}')
            data = response.json()
            
            exchange_rate = ExchangeRate(
                base=Currency(data.get('base')),
                rates=data.get('rates'),
            )
            
            self.currency_cache.put(exchange_rate)
            
            return exchange_rate
        

client = ExchangeRateApiClient()
currencies: List[Currency] = [Currency.EUR, Currency.USD, Currency.GBP]
times = []
for i in range(10):
    tic = time.perf_counter()
    rate: ExchangeRate = client.get_latest_rate(random.choice(currencies))
    toc = time.perf_counter()
    times.append(toc - tic)
pprint(f'Times w/o cache: {times}')

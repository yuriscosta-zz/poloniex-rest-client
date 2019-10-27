import logging
import json

from urllib.parse import urlencode
from hmac import new
from hashlib import sha512
from requests.exceptions import RequestException
from requests import post, get
from time import time

from exceptions import *


class Client(object):
    """The Poloniex Object!"""

    def __init__(self, key=False, secret=False, timeout=None):
        self.key = key
        self.secret = secret
        self.timeout = timeout
        self._nonce = int(
            "{:.6f}".format(time()).replace('.', '')
        )
        self.url_public = 'https://poloniex.com/public?command='
        self.url_private = 'https://poloniex.com/tradingApi'
        self.MINUTE, self.HOUR, self.DAY = 60, 60 * 60, 60 * 60 * 24
        self.WEEK, self.MONTH = self.DAY * 7, self.DAY * 30
        self.YEAR = self.DAY * 365

    @property
    def nonce(self):
        """ Increments the nonce"""
        print('nonce: ', self._nonce)
        return self._nonce

    ### Aux Methods ###
    def _has_credentials(self):
        if not self.key or not self.secret:
            raise PoloniexError("An Api Key and Secret needed!")

        return True

    def _login(self, params):
        login = new(self.secret.encode('utf-8'),
                    urlencode(params).encode('utf-8'),
                    sha512)

        headers = {'Sign': login.hexdigest(),
                   'Key': self.key}

        return headers

    def _generate_payload(self, params):
        payload = {'url': self.url_private,
                   'timeout': self.timeout,
                   'data': params,
                   'headers': self._login(params)}

        return payload

    def _do_post(self, params):
        params['nonce'] = self.nonce
        payload = self._generate_payload(params)
        response = post(**payload)

        return response.json()

    ### PUBLIC METHODS ###

    def returnTicker(self):
        url = self.url_public + 'returnTicker'
        response = get(url)

        return response.json()

    def return_24h_volume(self):
        url = self.url_public + 'return24hVolume'
        response = get(url)

        return response.json()

    def return_order_book(self, currency_pair='all', depth=20):
        params = {'currencyPair': currency_pair.upper(),
                  'depth': str(depth)}
        params = urlencode(params)
        url = self.url_public + 'returnOrderBook'
        response = get(url, params)

        return response.json()

    def market_trade_hist(self, currency_pair, start=None, end=None):
        params = {'currencyPair': currency_pair.upper()}

        if start:
            params['start'] = str(start)
        if end:
            params['end'] = str(end)

        params = urlencode(params)
        url = self.url_public + 'returnTradeHistory'
        response = get(url, params)

        return response.json()

    def return_chart_data(self, currency_pair, period=None, start=None, end=None):
        if period not in [300, 900, 1800, 7200, 14400, 86400]:
            raise PoloniexError("Invalid candle period: {}".format(period))

        if not start:
            start = time() - self.DAY
        if not end:
            end = time()

        params = {'currencyPair': currency_pair.upper(),
                  'period': str(period),
                  'start': str(start),
                  'end': str(end)}

        params = urlencode(params)
        url = self.url_public + 'returnTradeHistory'
        response = get(url, params)

        return response.json()

    def return_currencies(self):
        url = self.url_public + 'returnCurrencies'
        response = get(url)

        return response.json()

    def return_loan_orders(self, currency):
        params = {'currency': currency.upper()}
        params = urlencode(params)
        url = self.url_public + 'returnLoanOrders'
        response = get(url, params)

        return response.json()

    ### PRIVATE METHODS ###

    def return_balances(self):
        if self._has_credentials():
            params = {'command': 'returnBalances'}

            return self._do_post(params)

    def return_complete_balances(self, account='all'):
        if self._has_credentials():
            params = {'command': 'returnCompleteBalances',
                      'account': str(account)}

            return self._do_post(params)

    def return_deposit_addresses(self):
        if self._has_credentials():
            params = {'command': 'returnDepositAddresses'}

            return self._do_post(params)

    def generate_new_address(self, currency):
        if self._has_credentials():
            params = {'command': 'generateNewAddress',
                      'currency': currency}

            return self._do_post(params)

    def return_deposits_withdrawals(self, start=None, end=None):
        if self._has_credentials():
            if not start:
                start = time() - self.MONTH
            if not end:
                end = time()

            params = {'command': 'returnDepositsWithdrawals',
                      'start': str(start),
                      'end': str(end)}

            return self._do_post(params)

    def return_open_orders(self, currency_pair='all'):
        if self._has_credentials():
            params = {'nonce': self.nonce,
                      'command': 'returnOpenOrders',
                      'currencyPair': currency_pair.upper()}

            return self._do_post(params)

    def return_trade_history(self, currency_pair='all', start=None, end=None, limit=None):
        if self._has_credentials():
            params = {'command': 'returnTradeHistory',
                      'currencyPair': currency_pair.upper()}

            if start:
                params['start'] = start

            if end:
                params['end'] = end

            if limit:
                params['limit'] = limit

            return self._do_post(params)

    def return_available_account_balances(self, account=None):
        if self._has_credentials():
            params = {'command': 'returnAvailableAccountBalances'}
            if account:
                params['account'] = account

            return self._do_post(params)

    def return_tradable_balances(self):
        if self._has_credentials():
            params = {'command': 'returnTradableBalances'}

            return self._do_post(params)

    def return_open_loan_offers(self):
        if self._has_credentials():
            params = {'command': 'returnOpenLoanOffers'}

            return self._do_post(params)

    def return_order_trades(self, order_number):
        if self._has_credentials():
            params = {'command': 'returnOrderTrades',
                      'orderNumber': str(order_number)}

            return self._do_post(params)

    def return_active_loans(self):
        if self._has_credentials():
            params = {'command': 'returnActiveLoans'}

            return self._do_post(params)

    def return_lending_history(self, start=None, end=None, limit=None):
        if self._has_credentials():
            if not start:
                start = time() - self.MONTH
            if not end:
                end = time()

            params = {'command': 'returnLendingHistory',
                      'start': str(start),
                      'end': str(end)}
            if limit:
                params['limit'] = str(limit)

            return self._do_post(params)

    def create_loan_offer(self, currency, amount,
                          lending_rate, auto_renew=0, duration=2):
        if self._has_credentials():
            params = {'command': 'createLoanOffer',
                      'currency': currency.upper(),
                      'amount': str(amount),
                      'duration': str(duration),
                      'autoRenew': str(auto_renew),
                      'lendingRate': str(lending_rate)}

            return self._do_post(params)

    def cancel_loan_offer(self, order_number):
        if self._has_credentials():
            params = {'command': 'cancelLoanOffer',
                      'orderNumber': order_number}

            return self._do_post(params)

    def toggle_auto_renew(self, order_number):
        if self._has_credentials():
            params = {'command': 'toggleAutoRenew',
                      'orderNumber': order_number}

            return self._do_post(params)

    def buy(self, currency_pair, rate, amount, order_type=None):
        if self._has_credentials():
            params = {'command': 'buy',
                      'currencyPair': currency_pair.upper(),
                      'rate': str(rate),
                      'amount': str(amount)}

            if order_type:
                poss_types = ['fillOrKill', 'immediateOrCancel', 'postOnly']
                if not order_type in poss_types:
                    raise PoloniexError('Invalid orderType')
                params['orderType'] = 1

            return self._do_post(params)

    def sell(self, currency_pair, rate, amount, order_type=None):
        if self._has_credentials():
            params = {'command': 'sell',
                      'currencyPair': currency_pair.upper(),
                      'rate': str(rate),
                      'amount': str(amount)}

            if order_type:
                poss_types = ['fillOrKill', 'immediateOrCancel', 'postOnly']
                if not order_type in poss_types:
                    raise PoloniexError('Invalid orderType')
                params['orderType'] = 1

            return self._do_post(params)

    def cancel_order(self, order_number):
        if self._has_credentials():
            params = {'command': 'cancelOrder',
                      'orderNumber': order_number}

            return self._do_post(params)

    def move_order(self, order_number, rate, amount=None, order_type=None):
        if self._has_credentials():
            params = {'command': 'moveOrder',
                      'orderNuber': str(order_number),
                      'rate': str(rate)}

            if amount:
                params['amount'] = str(amount)
            if order_type:
                poss_types = ['immediateOrCancel', 'postOnly']
                if not order_type in poss_types:
                    raise PoloniexError(
                        'Invalid orderType: {}'.format(order_type))
                params['orderType'] = 1

            return self._do_post(params)

    def withdraw(self, currency, amount, address, payment_id=None):
        if self._has_credentials():
            params = {'command': 'withdraw',
                      'currency': currency.upper(),
                      'address': str(address)}

            if payment_id:
                params['paymentId'] = str(payment_id)

            return self._do_post(params)

    def return_fee_info(self):
        if self._has_credentials():
            params = {'command': 'returnFeeInfo'}

            return self._do_post(params)

    def transfer_balance(self, currency, amount,
                         from_account, to_account, confirmed=None):
        if self._has_credentials():
            params = {'command': 'transferBalance',
                      'currency': currency.upper(),
                      'amount': str(amount),
                      'fromAccount': str(from_account),
                      'toAccount': str(to_account)}

            if confirmed:
                params['confirmed'] = 1

            return self._do_post(params)

    def return_margin_account_summary(self):
        if self._has_credentials():
            params = {'command': 'returnMarginAccountSummary'}

            return self._do_post(params)

    def margin_buy(self, currency_pair, rate, amount, lending_rate=2):
        if self._has_credentials():
            params = {'command': 'marginBuy',
                      'currencyPair': currency_pair.upper(),
                      'rate': str(rate),
                      'amount': str(amount),
                      'lendingRate': str(lending_rate)}

            return self._do_post(params)

    def margin_sell(self, currency_pair, rate, amount, lending_rate=2):
        if self._has_credentials():
            params = {'command': 'marginSell',
                      'currencyPair': currency_pair.upper(),
                      'rate': str(rate),
                      'amount': str(amount),
                      'lendingRate': str(lending_rate)}

            return self._do_post(params)

    def get_margin_position(self, currency_pair='all'):
        if self._has_credentials():
            params = {'command': 'getMarginPosition',
                      'currencyPair': currency_pair.upper()}

            return self._do_post(params)

    def close_margin_position(self, currency_pair):
        if self._has_credentials():
            params = {'command': 'closeMarginPosition',
                      'currencyPair': currency_pair.upper()}

            return self._do_post(params)

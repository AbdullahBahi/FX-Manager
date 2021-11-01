#!/usr/bin/env python

"""
This module contains 'Account' class which is used for creating a fully functional virtual forex trading accounts.

used for trading simulation and strategies backtesting. first the user creates an account instance with the required paramaters, then this
instance is passed to fxmanager's built-in historical or live simulators. 

Classes:
    - Account: Class that simulates forex trading accounts.
"""

from numpy import inf
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

class Account():
    """
    Class that simulates forex trading accounts.
    
    Args:
        - balance         : float with initial balance in the account.
        - account_type    : string idicating account type, supported account types are
            - standard: lot size = 100,000
            - mini    : lot size = 10,000
            - micro   : lot size = 1000
            - nano    : lot size = 100
        - account_currency: string indicating the account currency (currency of initial balance).
        - leverage        : float indicating the leverage provided by the broker
        - volume_bounds   : tuple of 2 floats, minimum and maximum availabe trading volumes per one position.

    Public Methods:
        - open_pisition() : opens a new position and updates the state of the account accordingly.
        - close_position(): closes an opened position and updates the state of the account accordingly.
        - update()        : updates the state of the account (including oppened positions) with the current market prices.
    """

    def __init__(self, balance = 100000.0, account_type = 'standard', account_currency = 'usd', leverage = 0.01, volume_bounds = (0.01, 8.0)):
        ## constants
        LOT_SIZES = {"standard":100000.0, "mini":10000.0, "micro":1000.0, "nano":100.0}
        self._LOT_SIZE = LOT_SIZES[account_type.strip().lower()]
        self._LEVERAGE = leverage
        self._ACCOUNT_CURRENCY = account_currency.strip().lower()
        self._MIN_VOLUME = volume_bounds[0]
        self._MAX_VOLUME = volume_bounds[1]

        self._balance = balance ## account balance (updated every time a position is closed)
        self._equity = balance ## balance + closed_profit(updated every time a position is closed)
        self._live_equity = balance ## balance + live_profit (updated every time unit using close price)
        self._margin = 0.0 ## required deposit to hold current positionss (updated every time a position is opened  or closed)
        self._free_margin = balance ## equity - margin (updated every time a position is opened  or closed)
        self._live_free_margin = balance ## live equity - margin (updated every time unit using close price)
        self._margin_level = inf ## equity / margin (updated every time a position is opened  or closed)
        self._live_margin_level = inf ## live equity / margin (updated every time unit using close price)
        self._profit = 0.0 ## final profit (updated every time a position is closed)
        self._live_profit = 0.0 ## current profit  (updated every time unit using close price)
        # self._look_back_counter = {'AUDUSD':0, 'EURUSD':0, 'GBPUSD':0, 'NZDUSD':0, 'USDCAD':0, 'USDCHF':0, 'USDCHN':0, 'USDDKK':0, 'USDHKD':0, 'USDHUF':0, 'USDJPY':0, 'USDMXN':0, 'USDNOK':0, 'USDPLN':0, 'USDSEK':0, 'USDSGD':0, 'USDZAR':0}
        self._positions = {} ## dictionary to hold current positions {"Ticket":{..Position properties}, ..} (updated every time a position is opened or closed)
    
    def _get_lot_value(self, price, lot_size):
        return price * lot_size
    
    def _get_margin(self, lot_value, leverage, volume):
        return lot_value * leverage * volume
    
    def _get_profit(self, open_lot_value, close_lot_value, volume, order_type):
        order_types = {"sell":-1.0, "buy":1.0} ## must set profit to (close - open)
        return (close_lot_value - open_lot_value) * volume * order_types[order_type.strip().lower()]
    
    def open_pisition(self, ticket, base_currency, quote_currency, time_frame, weight, SL, TP, order_type, prices, period, order_idx, risk_factor=0.8):
        """
        opens a new position and updates the state of the account accordingly.
        """
        
        if not(base_currency.lower() != self._ACCOUNT_CURRENCY and quote_currency.lower() != self._ACCOUNT_CURRENCY):
            # FIRST GET OPEN PRICE
            price_types = {"sell":"bid", "buy":"ask"}
            open_price = prices[price_types[order_type]]
            if base_currency.lower() == self._ACCOUNT_CURRENCY:
                open_price = 1 / open_price

            # if price_types[order_type] == "buy":
            #     inc = 0.0001
            # else:
            #     inc = -0.0001
            # open_price += inc
            
            # NOW CALCULATE THE VOLUME
            # if self._look_back_counter[base_currency+quote_currency] < look_back:
            #     volume = 0.01
            #     self._look_back_counter[base_currency+quote_currency] +=1
            # else:
            max_margin = weight * self._balance ## maximum margin requirment that can be covered
            volume = (max_margin*risk_factor) / (open_price * self._LOT_SIZE * self._LEVERAGE)
            
            if volume < self._MIN_VOLUME:
                return False
            elif volume > self._MAX_VOLUME:
                volume = self._MAX_VOLUME
            else:
                pass

            # NOW UPDATE PORTFOLIO STATE
            ## 1 ## Margin
            open_lot_value = self._get_lot_value(open_price, self._LOT_SIZE)
            margin = self._get_margin(lot_value = open_lot_value, leverage = self._LEVERAGE, volume = volume)
            
            if self._balance < margin: ## if the current balance is less than the margin requirement >> don't open the position
                return False
            
            self._margin += margin

            ## 2 ## Free Margin
            self._free_margin = self._equity - self._margin

            ## 3 ## Margin Level
            if round(self._margin,2) == 0:
                self._margin_level = inf
            else:
                self._margin_level = round(self._equity,4) / round(self._margin,4)

            ## 4 ## Positions
            self._positions[ticket] = {
                'ticket': ticket,
                'order_idx': order_idx,
                'order_type': order_type,
                'volume': volume,
                'base_currency': base_currency,
                'quote_currency': quote_currency,
                'time_frame': time_frame,
                'open_price': open_price,
                'margin': margin,
                'SL': open_price - (SL * 0.001 * open_price), ## Formula: open_price - (SL * Maximum expected pip difference * open_price)
                'TP': open_price + (TP * 0.001 * open_price), ## Formula: open_price + (TP * Maximum expected pip difference * open_price)
                'live_profit': 0,
                'period': period,
                'weight': weight
            }
        
        else:
            print("\n>> PROCESS MESSAGE >> Position profit cannot be calculated! Currency pair must contain account currency.\n")
            return False
        return True
        

    def close_position(self, ticket, prices):
        """
        closes an opened position and updates the state of the account accordingly.
        """

        # FIRST GET POSITION PARAMETERS
        order_type = self._positions[ticket]['order_type']
        volume = self._positions[ticket]['volume']
        base_currency = self._positions[ticket]['base_currency']
        quote_currency = self._positions[ticket]['quote_currency']
        open_price = self._positions[ticket]['open_price']
        SL = self._positions[ticket]['SL']
        TP = self._positions[ticket]['TP']
        
        # NOW GET CLOSE PRICE
        price_types = {"sell":"ask", "buy":"bid"}
        close_price = prices[price_types[order_type]]
        if base_currency.lower() == self._ACCOUNT_CURRENCY:
            close_price = 1 / close_price

        # if price_types[order_type] == "buy":
        #     inc = -0.0001
        # else:
        #     inc = 0.0001
        # open_price += inc

        # NOW UPDATE PORTFOLIO STATE
        ## 1 ## Profit
        open_lot_value = self._get_lot_value(open_price, self._LOT_SIZE)
        close_lot_value = self._get_lot_value(close_price, self._LOT_SIZE)
        position_profit = self._get_profit(open_lot_value, close_lot_value, volume, order_type)
        self._profit += position_profit

        ## 2 ## balance
        self._balance += position_profit

        ## 3 ## Equity
        self._equity = self._balance

        ## 4 ## Margin
        margin = self._positions[ticket]['margin']
        self._margin -= margin

        ## 5 ## Free Margin
        self._free_margin = self._equity - self._margin

        ## 6 ## Margin Level
        if round(self._margin,2) == 0:
            self._margin_level = inf
        else:
            self._margin_level = round(self._equity,4) / round(self._margin,4)
        
        ## 7 ## Positions
        self._positions.pop(ticket)

        return position_profit, margin, close_price
    
    def update(self, prices):
        """
        updates the state of the account (including oppened positions) with the current market prices.
        """

        # UPDATE PORTFOLIO STATE
        ## 1 ## Live Profit & Periods
        self._live_profit = 0.0
        for i in self._positions:
            # Update Periods
            if self._positions[i]['period'] > 0:
                self._positions[i]['period'] -= 1

            # Get required position parameters
            order_type = self._positions[i]['order_type']
            volume = self._positions[i]['volume']
            base_currency = self._positions[i]['base_currency']
            quote_currency = self._positions[i]['quote_currency']
            cp = base_currency + quote_currency
            open_price = self._positions[i]['open_price']
            
            # Get current price
            price_types = {"sell":"ask", "buy":"bid"} ## note that bid and ask are reversed because it's a CLOSE price
            current_price = prices.iloc[-1][[cp+'_ask_close', cp+'_bid_close']]
            current_price.index = ['ask', 'bid']
            current_price = current_price[price_types[order_type]]
            
            if base_currency.lower() == self._ACCOUNT_CURRENCY:
                current_price = 1 / current_price

            # Calculate current profit
            open_lot_value = self._get_lot_value(open_price, self._LOT_SIZE)
            current_lot_value = self._get_lot_value(current_price, self._LOT_SIZE) ## base/quote lot value at if position is closed at current price
            live_profit = self._get_profit(open_lot_value, current_lot_value, volume, order_type)
            self._positions[i]['live_profit'] = live_profit
            self._live_profit += live_profit

        ## 2 ## Live Equity
        self._live_equity = self._balance + self._live_profit

        ## 3 ## Live Free Margin
        self._live_free_margin = self._live_equity - self._margin

        ## 4 ## Live Margin Level
        self._live_margin_level = self._live_equity / self._margin



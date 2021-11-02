#!/usr/bin/env python

"""
This module contains a class that is used by user to create a strategy object which is passed to fxmanager's built-in live and historical simulators.

Public Classes:
    - strategy_template: Class for injecting user defined trading strategies into fxmanager's built-in live and historical simulators.
"""

import pandas as pd
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

class strategy_template():
    """
    Class for injecting user defined trading strategies into fxmanager's built-in live and historical simulators.

    Args:
        - strategy       : reference to a user defined function for some trading strategy. The function MUST be structured as follows in order for the simulation to work proberly:  
                            - takes ONLY ONE positional argument called 'prices'. This argument is a pandas DataFrame with range index and the following columns:
                                - ask_open: open ask price of the candle stick.
                                - bid_open: open bid price of the candle stick.
                                - ask_close: close ask price of the candle stick.
                                - bid_close: close bid price of the candle stick.
                            - takes **kwargs for any other keword arguments.
                            - returns a pandas DataFrame with ONE RAW and the following columns:
                                - order_type: can be one of 3 values (buy, sell, hold)
                                - SL : stop loss.
                                - TP : take profit.
        - take_all_prices: boolean that controls the frequency of the range index of 'prices' DataFrame.  
                           If True:
                           all the prices history since the begining of the day is passed to the strategy function, the index is a normal range index (0, 1, 2, ...). the time difference between every reading is determined by the 'sleep_time' argument in the 'fxmanager.simulation.live.run()' or 'fxmanager.simulation.historic.run()' functions.
                           If False:
                           the frequncy of the prices becomes dependant on the time frame in which we want to generate an order, for examble, if we want to open a position in 'EURUSD' in the '5min' time frame, the index will become (0, 5, 10, ..).
    Methods:
        - get_orders: used in 'fxmanager.simulation.live.run()' and 'fxmanager.simulation.historic.run()' functions.
    """

    def __init__(self, strategy, take_all_prices = False):
        self._strategy = strategy
        self._currency_pair = ''
        self._time_frame = ''
        self._take_all_prices = take_all_prices

    def kwargs_template():
        """
        returns a template dictionary for keyword args used in used defined strategies. 
        """
        ## Replace keys and values with keys and values of the arguments required for your strategy.
        kwargs = {'arg_1_key':'arg_1_value',
                  'arg_2_key':'arg_2_value',
                  'arg_3_key':'arg_3_value'
                  }

        return kwargs

    def get_portfolios_template():
        """
        returns a list of dictionaries of length = num_days where each dictionary is a portfolio used for a given day.
        """
        
        ## Repeat the dictionaries to match the number of work days in the dataset and replace the values in the lists with the desired values
        ## for each day.
        ## If you want to use the same portfolio for all the days or you are using the live simulator, just fill the first dictionary and remove
        ## other dictionaries from the portfolios list.
        portfolios = [
                    {
                        'currency_pairs' : ['pair_1', 'pair_2', 'pair_3'], # replaced by a string of currency pair symbol
                        'time_frames' : ['tf_1', 'tf2', 'tf3'], # replaced by a string of '1min', '2min' or '10min' and so on.
                        'weights' : ['w1', 'w2', 'w3'] # replaced by floats that sum up to 1 (100%).
                    },
                    {
                        'currency_pairs' : ['pair_1', 'pair_2', 'pair_3'],
                        'time_frames' : ['tf_1', 'tf2', 'tf3'],
                        'weights' : ['w1', 'w2', 'w3']
                    },
                    ]
        
        return portfolios

    def template(prices, **kwargs):
        """
        function template for the user to build trading strategies.

        Args:
            - prices: pandas DataFrame with range index and the following columns:
                - ask_open: open ask price of the candle stick.
                - bid_open: open bid price of the candle stick.
                - ask_close: close ask price of the candle stick.
                - bid_close: close bid price of the candle stick.
            - kwargs: special dictionary to hold any number of required arguments for the function.
        
        Returns:
            - orders: pandas DataFrame with ONE RAW and the following columns:
                - order_type: can be one of 3 values (buy, sell, hold)
                - SL : stop loss.
                - TP : take profit.
        """
        
        # Step 1: Extract keyword arguments from keargs dictionary
        ##########################################################
        ##########################################################

        ## Your Code Here
        # Examble: to extract a keyword called 'foo'
        # foo = kwargs['foo']

        ##########################################################
        ##########################################################
        
        # Step 2: define the logic of the strategy
        ##########################################################
        ##########################################################

        ## Your Code Here (remove oreders = [])
        orders = []

        ##########################################################
        ##########################################################
        return orders

    def get_orders(self, prices, **kwargs):
        if self._take_all_prices:
            pc = pd.DataFrame({'ask_open': prices[self._currency_pair + '_ask_open'].values,
                               'bid_open': prices[self._currency_pair + '_bid_open'].values,
                               'ask_close': prices[self._currency_pair + '_ask_close'].values,
                               'bid_close': prices[self._currency_pair + '_bid_close'].values}, index = prices.index)
        else:
            if self._time_frame[1].isalpha():
                period = int(int(self._time_frame[0]))
            else:
                period = int(int(self._time_frame[:2]))
            pc = pd.DataFrame({'ask_open': prices.loc[(prices.index % period) == 0, self._currency_pair + '_ask_open'].values,
                            'bid_open': prices.loc[(prices.index % period) == 0, self._currency_pair + '_bid_open'].values,
                            'ask_close': prices.loc[(prices.index % period) == 0, self._currency_pair + '_ask_close'].values,
                            'bid_close': prices.loc[(prices.index % period) == 0, self._currency_pair + '_bid_close'].values},
                                index = prices.index[(prices.index % period) == 0])
        orders = self._strategy(prices=pc, **kwargs)
        return orders

if __name__ == '__main__':
    pass
#!/usr/bin/env python

"""
This module contains simple implementation of momentum trading strategy.

Public Functions:
    - get_orders(): sample trading strategy for purposes of testing live and historic trading simulators.
"""

import pandas as pd 
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

def get_orders(prices, **kwargs):
    """
    sample trading strategy for purposes of testing live and historic trading simulators.

    Args:
        - prices: pandas DataFrame with range index and a the following columns:
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

    look_back = kwargs['look_back']

    diff = prices['bid_close'] - prices['bid_open'] 
    
    if len(diff) < look_back:
        look_back = len(diff)

    diff_sum = diff.rolling(look_back+1).sum()
    up_trend_stregnth = diff_sum.loc[(diff_sum >= 0)]  
    down_trend_stregnth = diff_sum.loc[(diff_sum < 0)]

    # normalize stregnth
    up_trend_stregnth /= up_trend_stregnth.max()
    down_trend_stregnth /= down_trend_stregnth.min()

    orders = pd.DataFrame(index=diff_sum.index)
    
    orders.loc[(diff_sum >= 0), 'order_type'] = 'buy' 
    orders.loc[(diff_sum >= 0), 'SL'] = up_trend_stregnth
    orders.loc[(diff_sum >= 0), 'TP'] = up_trend_stregnth
    

    orders.loc[(diff_sum < 0), 'order_type'] = 'sell'
    orders.loc[(diff_sum < 0), 'SL'] = down_trend_stregnth
    orders.loc[(diff_sum < 0), 'TP'] = down_trend_stregnth

    orders.loc[diff_sum.isna(), 'order_type'] = ['hold']*(look_back) ## stupid positions 
    orders.loc[diff_sum.isna(), 'SL'] = [0]*(look_back) ## stupid positions 
    orders.loc[diff_sum.isna(), 'TP'] = [0]*(look_back) ## stupid positions 
    return orders

if __name__ == '__main__':
    # test case for get_orders_live
    prices = pd.DataFrame({'EURUSD_ask_open':[1.8,1.81,1.82,1,1,1,1,1,1,1],
                           'EURUSD_bid_open':[1.79,1.8,1.81,1,1,1,1,1,1,1],
                           'EURUSD_ask_close':[1.9,1.91,1.92,1,1,1,1,1,1,1],
                           'EURUSD_bid_close':[1.89,1.9,1.91,1,1,1,1,1,1,1],
                           'EURUSD_ask_open':[1.8,1.81,1.82,1,1,1,1,1,1,1],
                           'EURUSD_bid_open':[1.79,1.8,1.81,1,1,1,1,1,1,1],
                           'EURUSD_ask_close':[1.9,1.91,1.92,1,1,1,1,1,1,1],
                           'EURUSD_bid_close':[1.89,1.9,1.91,1,1,1,1,1,1,1]})
    orders = get_orders_live(prices, currency_pair='EURUSD', time_frame='10min', look_back=5)
    print(orders)
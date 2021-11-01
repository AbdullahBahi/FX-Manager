#!/usr/bin/env python

"""
This module contains helper functions used internally in this module and other modules in fxmanager's optimization sub-package. 

the functions defined in this module are designed for constructing optimal equally weighted portfolios. a portfolio consists of one or more assets where an asset in this context refers to a currency pair being traded in a specefic time frame.  
for example, if the currency pair 'EURUSD' is being traded in two different time frames, 5 and 10 minutes, where a new position is opened every 5 or 10 minutes, in this case the 'EURUSD_5min' and 'EURUSD_10min' are two different assets.

Public Functions:
    - optimize(): runs equally weighted portfolio optimization using data from a single day given an optimization method and objective.
        ** this function is designed to be used internally in 'fxmanager.optimization.eqw_optimization_test.run()' function. However, it can be used by the user separately to construct a portfolio for a given day without running the optimization test.
"""

from os import getcwd
from os.path import join
from itertools import combinations
import pandas as pd
import numpy as np
import fxmanager.basic.util as util
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

def mixed_timframes_portfolio(bestN, wrstN, objective='min_win_rate', print_progress=False):
    """
    Helper function for 'fxmanager.optimization.eq_weight_optimizer.optimize()' function.

    selects the optimal currency pair from each timeframe in the given data, then selects the optimal equally weighted combination of these timeframes.
    """

    num_assets = bestN.shape[1]
    assert  (len(bestN) >= num_assets) & (len(wrstN) >= num_assets)

    rows = combinations(range(bestN.shape[0]), num_assets)
    cols = bestN.columns.values
    
    w = np.array([1/num_assets,] * num_assets)

    optimized_W_R = 100
    optimized_R_R = 100
    c = 0
    for i, row in enumerate(rows):
        temp_df = bestN.loc[row, cols]
        diagonal = temp_df.to_numpy().diagonal()
        W_S_best = (w*diagonal).sum()
        temp_df = wrstN.loc[row, cols]
        diagonal = temp_df.to_numpy().diagonal()
        W_S_wrst = (w*diagonal).sum()
        
        W_R = (abs(W_S_wrst) / (W_S_best + abs(W_S_wrst)))
        R_R = abs(W_S_wrst) / W_S_best
        
        if objective == 'min_win_rate':
            if W_R < optimized_W_R:
                optimized_W_R = W_R
                optimized_R_R = R_R
                optimized_portfolio_idxs = row
        elif objective == 'min_risk_reward':
            if R_R < optimized_R_R:
                optimized_W_R = W_R
                optimized_R_R = R_R
                optimized_portfolio_idxs = row
        c += 1
        if print_progress:
            if i%500 == 0:
                print(f'>> PROCESS MESSAGE >> Finished: {round((c/ncr(bestN.shape[0], num_assets))*100, 2)}%     optimized_W_R: {round(optimized_W_R*100, 2)}%')
    if print_progress:
        print(f'>> PROCESS MESSAGE >> Finished: 100%     optimized_W_R: {round(optimized_W_R*100, 2)}%\n')
    
    optimized_portfolio_tfs = cols
    optimized_portfolio_weights = w
    
    return optimized_portfolio_idxs, optimized_portfolio_tfs, optimized_portfolio_weights, optimized_W_R, optimized_R_R

def single_timeframe_portfolio(best_tf, wrst_tf, num_assets, objective='min_win_rate', print_progress=False):
    """
    Helper function for 'fxmanager.optimization.eq_weight_optimizer.optimize()' function.

    selects the optimal equally weighted combination of currency pairs in the given timeframe data.
    """
    
    assert  (len(best_tf) >= 1) & (len(wrst_tf) >= 1)

    rows = combinations(range(best_tf.shape[0]), num_assets)
    cols = best_tf.columns.values
    
    w = np.array([1/num_assets] * num_assets)

    optimized_W_R = 100
    optimized_R_R = 100
    c = 0
    for i, row in enumerate(rows):
        W_S_best = (best_tf.loc[row, cols].to_numpy()*w).sum()
        W_S_wrst = (wrst_tf.loc[row, cols].to_numpy()*w).sum()

        W_R = (abs(W_S_wrst) / (W_S_best + abs(W_S_wrst)))
        R_R = abs(W_S_wrst) / W_S_best

        if objective == 'min_win_rate':
            if W_R < optimized_W_R:
                optimized_W_R = W_R
                optimized_R_R = R_R
                optimized_portfolio_idxs = row
        elif objective == 'min_risk_reward':
            if R_R < optimized_R_R:
                optimized_W_R = W_R
                optimized_R_R = R_R
                optimized_portfolio_idxs = row
        c += 1
        if print_progress:
            if i%500 == 0:
                print(f'>> PROCESS MESSAGE >> Finished: {round((c/ncr(best_tf.shape[0], num_assets))*100, 2)}%     optimized_W_R: {round(optimized_W_R*100, 2)}%')
    if print_progress:
        print(f'>> PROCESS MESSAGE >> Finished: 100%     optimized_W_R: {round(optimized_W_R*100, 2)}%\n')
    
    optimized_portfolio_tfs = cols
    optimized_portfolio_weights = w
    
    return optimized_portfolio_idxs, optimized_portfolio_tfs, optimized_portfolio_weights, optimized_W_R, optimized_R_R

def optimize(best_rets_df, wrst_rets_df, method='mixed_timeframes', objective='min_win_rate', test_run=True):
    """
    runs equally weighted portfolio optimization using data from a single day given an optimization method and objective.

    Args:
        - best_rets_df: pandas dataframe of average best return for each asset, columns are time_frames and index is a range index.
        - wrst_rets_df: pandas dataframe of average worst return for each asset, columns are time_frames and index is a range index.
        
        - method: string with optimization method to be used. The supported optimization methods are:
            - mixed_timeframes: selects the optimal currency pair from each available timeframe, then selects the optimal equally weighted combination of these time frames.
            - single_timeframe: selects the optimal time frame from the available timeframes, then selects the optimal equally weighted combination of currency pairs in the selected time frame.
        
        - objective: string with optimization objective to be used. The supported optimization objectives are:
            - min_win_rate   : minimizes the required win rate for the portfolio to acheive a positive returns.
            - min_risk_reward: minimizes the required risk reward ratio required for the portfolio to acheive a positive returns.
        
        - test_run: boolean flag used for testing purposes. If true, the constructed portfolios will consist of only one asset.

    Returns:
        - optimized_portfolio_idxs   : tuple with length equal to 'optimized_n' and values of integers that repesent the indices corresponding to the optimal currency pairs. 
        - optimized_portfolio_tfs    : numpy array with length of 'optimized_n' and values of optimal timeframes.
        - optimized_portfolio_weights: numpy array with length equal to 'optimized_n' and values of equal floats that sum up to 1.
        - optimized_n                : integer indicating the number of assets in the constructed portfolio.
        - optimized_W_R              : float indicating the minimum required win rate for the portfolio to acheive positive return.
        - optimized_R_R              : float indicating the minimum required risk reward for the portfolio to acheive positive return.

    ** this function is designed to be used internally in 'fxmanager.optimization.eqw_optimization_test.run()' function. However, it can be used by the user separately to construct a portfolio for a given day without running the optimization test.
    """

    num_tfs = best_rets_df.shape[1]
    num_cps = best_rets_df.shape[0]
    
    if method == 'mixed_timeframes':
        optimized_W_R = 100 ## Use any large initial value
        optimized_R_R = 100
        
        for n in range(1,num_tfs+1): # 109293 total iterations
            print(f'>> PROCESS MESSAGE >> Processing for n = {n} .. \n')
            top_n_tfs, _, __ = util.top_n_timeframes(best_rets_df, wrst_rets_df, objective=objective, n=n)
            portfolio_idxs, portfolio_cols, portfolio_weights, W_R, R_R = mixed_timframes_portfolio(best_rets_df[top_n_tfs],
                                                                                                    wrst_rets_df[top_n_tfs],
                                                                                                    objective=objective,
                                                                                                    print_progress=False)
            if objective == 'min_win_rate':
                if W_R < optimized_W_R:
                    optimized_W_R = W_R
                    optimized_R_R = R_R
                    optimized_portfolio_idxs = portfolio_idxs
                    optimized_portfolio_tfs = portfolio_cols
                    optimized_portfolio_weights = portfolio_weights
                    optimized_n = n
            elif objective == 'min_risk_reward':
                if R_R < optimized_R_R:
                    optimized_W_R = W_R
                    optimized_R_R = R_R
                    optimized_portfolio_idxs = portfolio_idxs
                    optimized_portfolio_tfs = portfolio_cols
                    optimized_portfolio_weights = portfolio_weights
                    optimized_n = n
            if test_run:
                break
    
    elif method == 'single_timeframe':
        optimized_W_R = 100 ## Use any large initial value
        optimized_R_R = 100
        top_n_tfs, _, __ = util.top_n_timeframes(best_rets_df, wrst_rets_df, objective=objective, n=1)
        
        for n in range(1,num_cps+1): # 131071 total iterations
            print(f'>> PROCESS MESSAGE >> Processing for n = {n} .. \n')
            # optimized_portfolio_idxs, optimized_portfolio_tfs, optimized_portfolio_weights, optimized_W_R, optimized_R_R
            portfolio_idxs, portfolio_cols, portfolio_weights, W_R, R_R = single_timeframe_portfolio(best_tf = best_rets_df[top_n_tfs],
                                                                                                    wrst_tf = wrst_rets_df[top_n_tfs],
                                                                                                    num_assets=n,
                                                                                                    objective=objective,
                                                                                                    print_progress=False)
            if objective == 'min_win_rate':
                if W_R < optimized_W_R:
                    optimized_W_R = W_R
                    optimized_R_R = R_R
                    optimized_portfolio_idxs = portfolio_idxs
                    optimized_portfolio_tfs = portfolio_cols
                    optimized_portfolio_weights = portfolio_weights
                    optimized_n = n
            elif objective == 'min_risk_reward':
                if R_R < optimized_R_R:
                    optimized_W_R = W_R
                    optimized_R_R = R_R
                    optimized_portfolio_idxs = portfolio_idxs
                    optimized_portfolio_tfs = portfolio_cols
                    optimized_portfolio_weights = portfolio_weights
                    optimized_n = n
            if test_run:
                break

    return optimized_portfolio_idxs, optimized_portfolio_tfs, optimized_portfolio_weights, optimized_n, optimized_W_R, optimized_R_R

if __name__ == '__main__':
    from fxmanager.basic.util import get_rets
    data_dir = join(getcwd(), '..','datasets')
    time_frames = ['1min', '2min', '3min', '4min', '5min', '6min', '7min', '8min', '9min', '10min']
    currency_pairs = ['AUDUSD', 'EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDCNH', 'USDDKK',
                  'USDHKD', 'USDHUF', 'USDJPY', 'USDMXN', 'USDNOK', 'USDPLN', 'USDSEK', 'USDSGD',
                  'USDZAR']
    d = 0
    best_rets_df, wrst_rets_df = get_rets(day=d, data_dir=data_dir, time_frames=time_frames, currency_pairs=currency_pairs)
    best_rets_df.index, wrst_rets_df.index = range(best_rets_df.shape[0]), range(best_rets_df.shape[0])
    
    optimized_portfolio_cps, optimized_portfolio_tfs, optimized_portfolio_weights, \
    optimized_n, optimized_W_R, optimized_R_R = optimize(best_rets_df,
                                                        wrst_rets_df,
                                                        data_dir=data_dir,
                                                        method='single_timeframe',
                                                        objective='min_win_rate',
                                                        test_run=False)
    print(f'Number of Assets Used in the Portfolio                : {optimized_n} Assets')
    print(f'Portfolio Currency Pairs                              : {optimized_portfolio_cps}')
    print(f'Portfolio Time Frames                                 : {optimized_portfolio_tfs}')
    print(f'Portfolio Weights                                     : {optimized_portfolio_weights}')
    print(f'Lowest Win Rate Required to get profit                : {round(optimized_W_R*100, 2)}%')
    print(f'Portfolio Risk-Reward ratio                           : {round(optimized_R_R*100, 2)}%')

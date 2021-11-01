#!/usr/bin/env python

"""
This module contains helper functions used internally in other fxmanager sub-packages. it also includes public functions to be used by the user to setup fxmanager project structure and pre-process the data.

Public Functions:
    - get_portfolios(): gets the portfolios to be used in historical backtesting of strategies.
    - setup()         : creates the required folders and files for any new project according to application type.
    - preprocess()    : preprocesses the raw data files to prepare it for analysis and simumlations.
"""

import sys
import json
from os import getcwd, mkdir, listdir
from os.path import join, isfile
from time import sleep
import operator as op
from functools import reduce
from shutil import copyfile
import inspect
from textwrap import dedent
import pandas as pd
import numpy as np
from fxmanager.strategies.template import strategy_template
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

def get_avg_rets(day, data_dir=None, time_frames=[], currency_pairs=[]):
    """
    gets the average best & worst returns of the passed currency pairs & timeframes from the preprocessed data in the 'data_dir\\time_frames' directory.

    Args:
        - day           : integer indicating day number - starts from 0 and ends with the total number of work days in the dataset.
        - data_dir      : string with the directory or full path to the directory in which application data is kept. If the setup() function is used to create the recommended project structure, the default None value should be used.
        - time_frames   : a list of strings of the timeframes from which the data is read.
        - currency_pairs: a list of strings of the currency pairs from which the data is read.
    
    Returns:
        - avg_best_rets: pandas dataframe of average best return for each asset, columns are time_frames and index is currency_pairs.
        - avg_wrst_rets: pandas dataframe of average worst return for each asset, columns are time_frames and index is currency_pairs.
    
    Usage:
        - used in 'fxmanager.simulation.live.run()' function if the construct_portfolio is set to True.
        - used in 'fxmanager.optimization.w_optimization_test' and 'fxmanager.optimization.eqw_optimization_test' modules.
    """

    if data_dir is None:
        data_dir = join(getcwd(), 'data')
    avg_best_rets = pd.DataFrame()
    avg_wrst_rets = pd.DataFrame()
    for i in time_frames:
        tf_rets = pd.DataFrame()
        for cp in currency_pairs:
            df = pd.read_csv(join(data_dir, 'time_frames', str(day), i , cp+'_'+i+'.csv'), parse_dates=True) 
            # Calculate average returns
            comp_best_rets = (df['best_rets']).mean()
            comp_wrst_rets = (df['wrst_rets']).mean()
            
            tf_rets[cp] = pd.Series({'comp_best_rets':comp_best_rets,
                                     'comp_wrst_rets':comp_wrst_rets
                                    })
        avg_best_rets[i] = tf_rets.loc['comp_best_rets']
        avg_wrst_rets[i] = tf_rets.loc['comp_wrst_rets']
        
    return avg_best_rets, avg_wrst_rets

def get_portfolios(data_dir=None, num_days=1, single_portfolio={}, portfolios=[], optimized_portfolios=False, use_single_porfolio=False):
    """
    gets the portfolios to be used in historical backtesting of strategies.

    Args:
        - data_dir        : string with the directory or full path to the directory in which application data is kept. If the setup() function is used to create the recommended project structure, the default None value should be used.
        - num_days        : total number of work days in the dataset.
        - single_portfolio: dictionary of the portfolio to be used for backtesting with keys (currency_pairs, time_frames, weights) used if 'optimized_portfolios' is False and 'use_single_porfolio' is True.
        - portfolios      : list of dictionries like 'single_portfolio'. Lenght of the list = num_days-1. used if 'optimized_portfolios' is False and 'use_single_porfolio' is False.
        - optimized_portfolios: boolean flag, set to True if an optimization test is run and the portfolios to be used are saved in 'data_dir\\stats\\Optimizer_Test_portfolios.csv' file.
        - use_single_porfolio: boolean flag, used if 'optimized_portfolios' is False, set to true if you passed a single portfolio in the 'single_portfolio' argument, if False, 'portfolios' argument is used instead.
    
    Returns:
        - df: pandas dataframe with columns (currency_pairs, time_frames, weights) and range index of length = num_days
    
    Usage:
        - used by user before calling the function 'fxmanager.simulation.historic.run()'. 
    """

    if data_dir is None:
        data_dir = join(getcwd(), 'data')
    if optimized_portfolios:
        df = pd.read_csv(join(data_dir, 'stats', 'Optimizer_Test_portfolios.csv'), parse_dates=True)
        currency_pairs, time_frames, weights = [], [], []
        for idx in df.index:
            cps = [cp.strip('\'') for cp in df.loc[idx, 'currency_pairs'].lstrip('[').rstrip(']').split(',')]
            tfs = [tf.strip('\'') for tf in df.loc[idx, 'time_frames'].lstrip('[').rstrip(']').split(',')]
            w = [float(w) for w in df.loc[idx, 'weights'].lstrip('[').rstrip(']').split(',')]
            currency_pairs.append(cps)
            time_frames.append(tfs)
            weights.append(w)
        df = pd.DataFrame({'currency_pairs': currency_pairs,
                           'time_frames': time_frames,
                           'weights': weights
                          })
        df.index.name='days'
        
    else:
        if use_single_porfolio:
            df = pd.DataFrame([single_portfolio]*num_days)
            df.index.name='days'
        else:
            df = pd.DataFrame(portfolios)
            df.index.name='days'
    return df

def get_weights(data_dir=None, num_assets=1):
    """
    reads the pre-calculated weights from 'data_dir\\weights\\' directory to be used for weight optimization.

    Args:
        - data_dir   : string with the directory or full path to the directory in which application data is kept. If the setup() function is used to create the recommended project structure, the default None value should be used.
        - num_assets : number of assets in the portfolio being optimized. An asset is a currency pair in a specific timeframe.
    
    Returns:
        - weight_combinations_list: list of all possible weight combinations for the passed number of assets.
    
    Usage:
        - used in 'fxmanager.optimization.weight_optimizer' module.
    """

    if data_dir is None:
        data_dir = join(getcwd(), 'data')
    weight_combinations_list = []
    weight_file_name = str(num_assets)+'_asset_weights.txt'
    with open(join(data_dir,'weights',weight_file_name),'r') as f:
        lines = f.readlines()
        for line in lines:
            line = [float(w) for w in line[:-2].split(',')]
            while len(line) < num_assets:
                line.append(0)
            weight_combinations_list.append(line)
    
    return weight_combinations_list

def top_n_timeframes(best, wrst, objective='min_win_rate', n=1):
    """
    selects the best (n) of time frames according to the 'objective' argument.

    Args:
        - best     : pandas dataframe with the return of the 'get_avg_rets()' function defined above. note tha the index must be transformed first to range index.
        - wrst     : pandas dataframe with the return of the 'get_avg_rets()' function defined above. note tha the index must be transformed first to range index.
        - objective: string indecating the criteria with which the best time frames will be chosed, supported objectives are (min_win_rate, min_risk_reward)
        - n        : integer indicating the number of time frames to return
    
    Returns:
        - top_n: numpy array with the names of selected best time frames.
        - W_R  : pandas series with required win rates for every time frame.
        - R_R  : pandas series with required risk rewards for every time frame.
    
    Usage:
        - used in 'fxmanager.optimization.weight_optimizer' and 'fxmanager.optimization.eq_weight_optimizer' modules.
    """

    num_cps = best.shape[0]

    weights = [1/num_cps,] * num_cps
    weights_df = pd.DataFrame(weights,columns=['W'])
    W_S_best = best.multiply(weights_df['W'], axis=0).sum(axis=0)
    W_S_wrst = wrst.multiply(weights_df['W'], axis=0).sum(axis=0)
    W_R = (abs(W_S_wrst) / (W_S_best + abs(W_S_wrst)))
    R_R = abs(W_S_wrst) / W_S_best

    if objective == 'min_win_rate':
        top_n = W_R.nsmallest(n).index.values
        return top_n, W_R, R_R
    elif objective == 'min_risk_reward':
        top_n = R_R.nsmallest(n).index.values
        return top_n, W_R, R_R

def findCombinationsUtil(arr, index, num, reducedNum):
    """
    helper function for findCombinations() function.
    """

    # Base condition
    if (reducedNum < 0):
        return

    if (reducedNum == 0):
        for i in range(index):
            print(arr[i], end = ",")
        print("")
        return
 
    prev = 1 if(index == 0) else arr[index - 1]
 
    for k in range(prev, num + 1):
        arr[index] = k
        findCombinationsUtil(arr, index + 1, num,
                                 reducedNum - k)
 
def findCombinations(n):
    """
    finds all possible combinations that sum up to n.

    Args:
        - n: integer idicating the number that returned cambinations sum up to.
    
    Returns:
        - every combination is printed in a new line to standard output. to save the results to a file, change sys.stdout to the path of the file.
    
    Usage:
        - used in 'fxmanager.basic.util.setup()' function to save required weight combinations to 'data_dir\\weigts' directory.
    """

    arr = [0] * n
    findCombinationsUtil(arr, 0, n, n)

def ncr(n, r):
    """
    calculates the number of combinations nCrز
    
    Args:
        - n: integer indicating the total number of items to be combined.
        - r: integer indicating the length of every combination.
    
    Returns:
        - res: integer with the result.
    """

    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    res = numer // denom
    return res

def expected_return(day=0, data_dir=None, time_frames=[], currency_pairs=[], weights=[], leverage=0.01, win_rate=0.5, risk_reward=1, n_scenarios=100):
    """
    calculates the average expected daily return from a portfolio given a win rate and a risk-reward ratio.

    Args:
        - day           : integer with range from 0 to (number of working days in the dataset-1).
        - data_dir      : string with the directory or full path to the directory in which application data is kept. If the setup() function is used to create the recommended project structure, the default None value should be used.
        - time_frames   : list of portfolio timeframes.
        - currency_pairs: list of portfolio currency pairs.
        - weights       : list of portfolio weights.
        - leverage      : float indicating the leverage. if no leverage is used set to 1.
        - win_rate      : float indicating the percentage of winning positions to the total number of positions.
        - risk_reward   : float indicating ratio of reward to risk.
        - n_scenarios   : integer indicating the number of scenarios across which the expected return is averaged.
    
    Returns:
        - avg_expected_return: float indicating the average expected return.
        - win_probability    : float indicating the ratio of number of scenarios in which the expected return is positive to the total number
                               of scenarios.
    
    Usage:
        - used in 'fxmanage.optimization.eqw_optimization_test.run_test()' function to calculate the expected returns using the optimized 
          portfolios.
    """

    if data_dir is None:
        data_dir = join(getcwd(), 'data')
    if win_rate > 1:
        win_rate = 1
    loss_rate = 1 - win_rate
    num_assets = len(time_frames) # or len(currency_pairs), both are the same

    er = 0
    win_probability = 0
    for i in range(n_scenarios):
        scenario_rets = 0
        for tf, cp, weight in zip(time_frames, currency_pairs, weights):
            file_name = cp + '_' + tf + '.csv'
            df = pd.read_csv(join(data_dir, 'time_frames', str(day), tf, file_name))
            df.loc[:, ('best_rets', 'wrst_rets')] /= leverage
            num_wins = int(win_rate * df.shape[0])
            num_losses = df.shape[0] - num_wins
            if num_wins > df.shape[0]:
                num_wins = df.shape[0]
                num_losses = 0
            if risk_reward > 1: ## Risk is more than reward >> take 100% from loss samples and 1/risk_reward from win samples
                sampled_win_rets = df['best_rets'].sample(num_wins)*weight*(1/risk_reward)
                sampled_loss_rets = df['wrst_rets'].sample(num_losses)*weight
            elif risk_reward < 1:
                sampled_win_rets = df['best_rets'].sample(num_wins)*weight
                sampled_loss_rets = df['wrst_rets'].sample(num_losses)*weight*risk_reward
            else:
                sampled_win_rets = df['best_rets'].sample(num_wins)*weight
                sampled_loss_rets = df['wrst_rets'].sample(num_losses)*weight

            rets = pd.concat([sampled_win_rets, sampled_loss_rets], ignore_index=True)
            scenario_rets += (1+rets).prod()-1

        er += scenario_rets
        if scenario_rets > 0:
            win_probability += (1/n_scenarios)
    avg_expected_return = er/n_scenarios
    return avg_expected_return, win_probability

def setup(app_type='', raw_data_dir='', live_raw_data_dir='', raw_data_type='', file_name_format='', num_days=1, num_cps=1, num_tfs=1):
    """
    creates the required folders and files for any new project according to application type.

    Args:
        - app_type : string indicating the application type. supported app types are:
            - back_tester          : if you want to test trading strategies using histoical data on FX-Manager virtual account.
            - portfolio_optimizer  : if you want to asses different portfolio optimization methods and objectives using histoical data.
            - live_simulator       : if you want to test trading strategies in real time using MT4 Live data on FX-Manager virtual account.
            - all_in_one           : if you want to use all the previous features.
        
        - raw_data_dir     : string containig the path to directory in which the raw data files are kept.
        - live_raw_data_dir: string containig the path to directory in which the raw data files from the previous day are kept. used to construct a portfolio using built-in fxmanager optimization for live simulation.
        
        - raw_data_type : string with the type of raw data used, supported raw data types are: 
            - daily_bid_ask  : Bid/Ask ticks in daily seperate files (a file for each currency_pair in each day)
            - daily_candles  : 1-min candles in daily seperate files (a file for each currency_pair in each day)
            - period_candles : 1-min candles over a period (a file for each currency_pair for all the days)
        
        - file_name_format : string of white spaces with the same length as raw data file names. Givin that each file name has information about date and currency pair symbol, the white spaces in the same location as these information are replaced as follows:
            - day, month and year in the date are replaced with (dd), (mm), (yyyy) respectively.
            - currency pair symbol is replaced with (cccccc).
            ** for example, if the file name is 'AUDUSD_Ticks_02.08.2021-02.08.2021.csv' then the file_name_format is: 'cccccc       dd mm yyyy               '
                                         
        - num_days         : total number of work days in the dataset.
        - num_cps          : integer indicating the number of currency pairs in the dataset
        - num_tfs          : integer indicating the number of timeframes in the dataset.
    
    """

    print('\n>> SYSTEM MESSAGE >> STAGE 1: Creating Necessary Folders And Files ..\n')

    cwd = getcwd()
    raw_data_formats = {
        "daily_bid_ask" : {
            "date_col"    : "Gmt time",
            "date_format" : "%d.%m.%Y %H:%M:%S.%f",
            "ask_col"     : "Ask",
            "bid_col"     : "Bid"
        },

        "daily_candles" : {
            "date_col"      : "time",
            "date_format"   : "%Y.%m.%d %H:%M",
            "open_col"      : "open",
            "high_col"      : "high",
            "low_col"       : "low",
            "close_col"     : "close",
            "tick_vol_col"  : "tick_volume"
        },

        "period_candles" : {
            "date_col"       : "time",
            "date_format"    : "%Y.%m.%d %H:%M",
            "open_col"       : "open",
            "high_col"       : "high",
            "low_col"        : "low",
            "close_col"      : "close",
            "tick_vol_col"   : "tick_volume"
        }  
    }
    json_object = json.dumps(raw_data_formats, indent = 4)
    with open("raw_data_formats.json", "w") as outfile:
        outfile.write(json_object)
    
    # create strategy.py file
    lines = inspect.getsource(strategy_template.template)
    with open('strategy.py', 'w') as f:
        f.write(dedent(lines))
    
    # add keyword arguments to strategy.py file
    lines = inspect.getsource(strategy_template.kwargs_template)
    with open('strategy.py', 'a') as f:
        f.write(dedent(lines))
    
    # add portfilios to strategy.py file
    lines = inspect.getsource(strategy_template.get_portfolios_template)
    with open('strategy.py', 'a') as f:
        f.write(dedent(lines))
    
    mkdir(join(cwd,'data'))
    mkdir(join(cwd,'data', 'logs'))
    mkdir(join(cwd,'data', 'visualizations'))
    mkdir(join(cwd,'data', 'stats'))
    mkdir(join(cwd,'data', 'raw_data'))
    mkdir(join(cwd,'data', 'raw_data_archive'))
    mkdir(join(cwd,'data', 'time_frames'))
    mkdir(join(cwd,'data', 'weights'))
    
    for i in range(1, max(num_cps, num_tfs)+1):
        sys.stdout = open(join(cwd,'data', 'weights', str(i)+'_asset_weights.txt'), 'w')
        findCombinations(i)
        sys.stdout.close()
    sys.stdout = sys.__stdout__
    
    if app_type == 'back_tester' or app_type == 'portfolio_optimizer' or app_type == 'all_in_one':
        for i in range(num_days):
            mkdir(join(cwd,'data', 'time_frames', str(i)))
            for j in range(1,num_tfs+1):
                mkdir(join(cwd,'data', 'time_frames', str(i), str(j)+'min'))
        if app_type == 'back_tester':
            mkdir(join(cwd,'data', 'stats', 'historical_simulation_orders'))
        if app_type == 'all_in_one':
            mkdir(join(cwd,'data', 'stats', 'historical_simulation_orders'))
            mkdir(join(cwd,'data', 'live_data'))
            mkdir(join(cwd,'data', 'live_data', 'raw_data'))
            mkdir(join(cwd,'data', 'live_data', 'time_frames'))
            for i in range(1,num_tfs+1):
                mkdir(join(cwd,'data', 'live_data', 'time_frames', str(i)+'min'))
            
            raw_file_names = [f for f in listdir(live_raw_data_dir)]
            for file_name in raw_file_names:
                currency_pair = ''.join([file_name[n] for n,m in enumerate(file_name_format) if m =='c'])
                new_file_name = currency_pair + '.csv'
                copyfile(join(live_raw_data_dir,file_name), join(cwd,'data', 'live_data', 'raw_data', new_file_name))

        print('>> SYSTEM MESSAGE >> All Necessary Folders And Files Are Created Successfully! ..\n')
        print('>> SYSTEM MESSAGE >> STAGE 2: Coppying Raw Data Files ..\n')
        
        raw_file_names = [f for f in listdir(raw_data_dir)]
        if raw_data_type == 'daily_bid_ask' or raw_data_type == 'daily_candles':
            dates = []
            for file_name in raw_file_names:
                day = ''.join([file_name[i] for i,m in enumerate(file_name_format) if m =='d'])
                month = ''.join([file_name[i] for i,m in enumerate(file_name_format) if m =='m'])
                year = ''.join([file_name[i] for i,m in enumerate(file_name_format) if m =='y'])
                dates.append(month+'.'+day+'.'+year)
            sorted_file_names = pd.DataFrame(raw_file_names, index=pd.to_datetime(dates), columns=[0]).sort_index()
            unique_dates = set(dates)
            unique_dates_sorted = pd.DataFrame([0]*num_days, index=pd.to_datetime(list(unique_dates))).sort_index().index
                        
            for i, idx in enumerate(unique_dates_sorted):
                print(f'>> PROCESS MESSAGE >> Coppying Data Of Day {i} ..')
                mkdir(join(cwd,'data', 'raw_data', str(i)))
                for file_name in sorted_file_names.loc[idx,0]:
                    if num_cps == 1:
                        file_name = sorted_file_names.loc[idx,0]
                    # move files
                    currency_pair = ''.join([file_name[n] for n,m in enumerate(file_name_format) if m =='c'])
                    day = ''.join([file_name[i] for i,m in enumerate(file_name_format) if m =='d'])
                    month = ''.join([file_name[i] for i,m in enumerate(file_name_format) if m =='m'])
                    year = ''.join([file_name[i] for i,m in enumerate(file_name_format) if m =='y'])
                    new_file_name = currency_pair + '_' + str(pd.to_datetime([month+'.'+day+'.'+year])[0].date()) + '.csv'
                    copyfile(join(raw_data_dir,file_name), join(cwd,'data', 'raw_data', str(i), new_file_name))
                    if num_cps == 1:
                        break 
        
        elif raw_data_type == 'period_candles':
            for file_name in raw_file_names:
                currency_pair = ''.join([file_name[n] for n,m in enumerate(file_name_format) if m =='c'])
                new_file_name = currency_pair + '.csv'
                copyfile(join(raw_data_dir,file_name), join(cwd,'data', 'raw_data', new_file_name))
        else:
            pass
        
        print('\n>> SYSTEM MESSAGE >> All Raw Data Files Are Coppied Successfully! ..\n')
    
    elif app_type == 'live_simulator':
        for i in range(1,num_tfs+1):
            mkdir(join(cwd,'data', 'time_frames', str(i)+'min'))
        
        print('>> SYSTEM MESSAGE >> All Necessary Folders Are Created Successfully! ..\n')
        print('>> SYSTEM MESSAGE >> STAGE 2: Coppying Raw Data Files ..\n')

        raw_file_names = [f for f in listdir(live_raw_data_dir)]
        for file_name in raw_file_names:
            currency_pair = ''.join([file_name[n] for n,m in enumerate(file_name_format) if m =='c'])
            new_file_name = currency_pair + '.csv'
            copyfile(join(live_raw_data_dir,file_name), join(cwd,'data', 'raw_data', new_file_name))

        print('>> SYSTEM MESSAGE >> All Raw Data Files Are Coppied Successfully! ..\n')
  
    else:
        pass
    
    print('>> SYSTEM MESSAGE >> Finishing ..\n')

def process_daily_bid_ask(df, tf):
    """
    helper function for 'fxmanager.basic.util.preprocess()' function.
    
    used to group the given Bid/Ask data by the given timeframe and calculate open and close prices for the new candle sticks in the new timeframe.
    """
    # initialize placeholders for final data
    ask_open = []
    bid_open = []
    ask_close = []
    bid_close = []
    ask_high = []
    bid_high = []
    ask_low	= []
    bid_low = []
    ask_sample1 = []
    bid_sample1 = []
    ask_sample2 = []
    bid_sample2 = []
    best_rets = []
    wrst_rets = []
    tick_volume = []

    # get a DataFrame that is grouped by the specified timeframe
    grouped = pd.DataFrame(df.groupby(pd.Grouper(freq=tf)), columns=['time', 'sub_dataframes'])

    for dataframe in grouped['sub_dataframes']:
        tick_volume.append(dataframe.shape[0])
        if dataframe.shape[0] != 0:
            ask_open.append(dataframe['ask'][0])
            bid_open.append(dataframe['bid'][0])
            ask_close.append(dataframe['ask'][-1])
            bid_close.append(dataframe['bid'][-1])
            ask_high.append(dataframe['ask'].max())
            bid_high.append(dataframe['bid'].max())
            ask_low.append(dataframe['ask'].min())
            bid_low.append(dataframe['bid'].min())
            
            delta_t = (dataframe.index[-1]-dataframe.index[0])/2
            open_plus_delta = delta_t + dataframe.index[0]
            idx_diff = dataframe.index - open_plus_delta
            pos_idx_diff = [a for a in idx_diff if a.days==0]
            idx = min(pos_idx_diff) + open_plus_delta

            ask_sample1.append(dataframe.loc[dataframe.index[0]:idx]['ask'].sample().values[0])
            bid_sample1.append(dataframe.loc[dataframe.index[0]:idx]['bid'].sample().values[0])
            ask_sample2.append(dataframe.loc[idx:dataframe.index[-1]]['ask'].sample().values[0])
            bid_sample2.append(dataframe.loc[idx:dataframe.index[-1]]['bid'].sample().values[0])
            
            if bid_high[-1] > ask_low[-1]:
                ## if minimum ask price comes first >> buy >> devide by ask_low
                if max(dataframe['bid'].idxmax(), dataframe['ask'].idxmin()) == dataframe['bid'].idxmax():
                    best_rets.append((bid_high[-1]-ask_low[-1]) / ask_low[-1])
                    wrst_rets.append((bid_low[-1]-ask_high[-1]) / bid_low[-1])
                ## if maximum bid price comes first >> sell >> devide by bid_high
                else:
                    best_rets.append((bid_high[-1]-ask_low[-1]) / bid_high[-1])
                    wrst_rets.append((bid_low[-1]-ask_high[-1]) / ask_high[-1])

            else:
                best_rets.append(0)
                if max(dataframe['bid'].idxmin(), dataframe['ask'].idxmax()) == dataframe['bid'].idxmin():
                    wrst_rets.append((bid_low[-1]-ask_high[-1]) / bid_low[-1])
                else:
                    wrst_rets.append((bid_low[-1]-ask_high[-1]) / ask_high[-1])
            
        else:
            ask_open.append(ask_close[-1])
            bid_open.append(bid_close[-1])
            ask_close.append(ask_close[-1])
            bid_close.append(bid_close[-1])
            ask_high.append(ask_close[-1])
            bid_high.append(bid_close[-1])
            ask_low.append(ask_close[-1])
            bid_low.append(bid_close[-1])
            ask_sample1.append(ask_close[-1])
            bid_sample1.append(bid_close[-1])
            ask_sample2.append(ask_close[-1])
            bid_sample2.append(bid_close[-1])
            best_rets.append(0)
            wrst_rets.append((bid_low[-1]-ask_high[-1]) / bid_low[-1])

    final_df = pd.DataFrame({'best_rets':best_rets,
                             'wrst_rets':wrst_rets,
                             'ask_open':ask_open,
                             'bid_open':bid_open,
                             'ask_close':ask_close,
                             'bid_close':bid_close,
                             'ask_sample1':ask_sample1,
                             'bid_sample1':bid_sample1,
                             'ask_sample2':ask_sample2,
                             'bid_sample2':bid_sample2,
                             'tick_volume':tick_volume
                            }, index=pd.to_datetime(grouped['time']))
    return final_df

def process_ohlc(df, tf):
    """
    helper function for 'fxmanager.basic.util.preprocess()' function.

    used to group the given OHLCV data by the given timeframe and calculate open and close prices for the new candle sticks in the new timeframe.
    """

    # initialize placeholders for final data
    ask_open = []
    bid_open = []
    ask_close = []
    bid_close = []
    ask_high = []
    bid_high = []
    ask_low	= []
    bid_low = []
    ask_sample1 = []
    bid_sample1 = []
    ask_sample2 = []
    bid_sample2 = []
    best_rets = []
    wrst_rets = []
    tick_volume = []

    # Calculate spread using Corwin-Schultz model
    l = df['low']
    h = df['high']
    gamma = (np.log(h.rolling(2).max()/l.rolling(2).min()))**2
    beta = (np.log(h/l))**2 + (np.log(h.shift(1)/l.shift(1)))**2
    alpha = ((np.sqrt(2*beta) - np.sqrt(beta)) / (3-(2*np.sqrt(2)))) - np.sqrt(gamma / (3-(2*np.sqrt(2))))
    s = 2*(np.exp(alpha)-1) / (1+np.exp(alpha))
    s = abs(s).round(5)
    s[0] = s[1]

    # Add bid/ask column to df 
    df = pd.DataFrame({'bid_open': df['open'].values,
                       'ask_open': (df['open'].to_numpy()+s).round(5),
                       'bid_close': df['close'].values,
                       'ask_close': (df['close'].to_numpy()+s).round(5),
                       'bid_high': df['high'].values,
                       'ask_high': (df['high'].to_numpy()+s).round(5),
                       'bid_low': df['low'].values,
                       'ask_low': (df['low'].to_numpy()+s).round(5),
                       'tick_volume':df['tick_volume'].values}, index=df.index)
    # get a DataFrame that is grouped by the specified timeframe
    grouped = pd.DataFrame(df.groupby(pd.Grouper(freq=tf)), columns=['time', 'sub_dataframes'])

    for dataframe in grouped['sub_dataframes']:
        tick_volume.append(dataframe['tick_volume'].sum())
        ask_open.append(dataframe['ask_open'][0])
        bid_open.append(dataframe['bid_open'][0])
        ask_close.append(dataframe['ask_close'][-1])
        bid_close.append(dataframe['bid_close'][-1])
        ask_high.append(dataframe['ask_high'].max())
        bid_high.append(dataframe['bid_high'].max())
        ask_low.append((dataframe['ask_low'].min()))
        bid_low.append(dataframe['ask_low'].min())
        
        delta_t = (dataframe.index[-1]-dataframe.index[0])/2
        open_plus_delta = delta_t + dataframe.index[0]
        idx_diff = dataframe.index - open_plus_delta
        pos_idx_diff = [a for a in idx_diff if a.days==0]
        idx = min(pos_idx_diff) + open_plus_delta

        ask_sample1.append(dataframe.loc[:idx]['ask_open'].sample().values[0])
        bid_sample1.append(dataframe.loc[:idx]['bid_open'].sample().values[0])
        ask_sample2.append(dataframe.loc[idx:]['ask_close'].sample().values[0])
        bid_sample2.append(dataframe.loc[idx:]['bid_close'].sample().values[0])
        
        if bid_high[-1] > ask_low[-1]:
            ## if minimum ask price comes first >> buy >> devide by ask_low
            if max(dataframe['bid_high'].idxmax(), dataframe['ask_low'].idxmin()) == dataframe['bid_high'].idxmax():
                best_rets.append((bid_high[-1]-ask_low[-1]) / ask_low[-1])
                wrst_rets.append((bid_low[-1]-ask_high[-1]) / bid_low[-1])
            ## if maximum bid price comes first >> sell >> devide by bid_high
            else:
                best_rets.append((bid_high[-1]-ask_low[-1]) / bid_high[-1])
                wrst_rets.append((bid_low[-1]-ask_high[-1]) / ask_high[-1])
        else:
            best_rets.append(0)
            # print(dataframe, end='\n\n')
            if max(dataframe['bid_low'].idxmin(), dataframe['ask_high'].idxmax()) == dataframe['bid_low'].idxmin():
                wrst_rets.append((bid_low[-1]-ask_high[-1]) / bid_low[-1])
            else:
                wrst_rets.append((bid_low[-1]-ask_high[-1]) / ask_high[-1])

    final_df = pd.DataFrame({'best_rets':best_rets,
                             'wrst_rets':wrst_rets,
                             'ask_open':ask_open,
                             'bid_open':bid_open,
                             'ask_close':ask_close,
                             'bid_close':bid_close,
                             'ask_sample1':ask_sample1,
                             'bid_sample1':bid_sample1,
                             'ask_sample2':ask_sample2,
                             'bid_sample2':bid_sample2,
                             'tick_volume':tick_volume
                            }, index=pd.to_datetime(grouped['time']))
    return final_df

def preprocess(data_dir=None, app_type='', raw_data_type='', raw_data_format={}, save_logs=True):
    """
    preprocesses the raw data files to prepare it for analysis and simumlations.

    Args:
        - data_dir : string with the directory or full path to the directory in which application data is kept. If the setup() function is used to create the recommended project structure, the default None value should be used.

        - app_type : string indicating the application type. supported app types are
            - back_tester          : if you want to test trading strategies using histoical data on FX-Manager virtual account.
            - portfolio_optimizer  : if you want to asses different portfolio optimization methods and objectives using histoical data.
            - live_simulator       : if you want to test trading strategies in real time using MT4 Live data on FX-Manager virtual account.
            - all_in_one           : if you want to use all the previous features.
        
        - raw_data_type : string with the type of raw data used, supported raw data types are
            - daily_bid_ask  : Bid/Ask ticks in daily seperate files (a file for each currency_pair in each day)
            - daily_candles  : 1-min candles in daily seperate files (a file for each currency_pair in each day)
            - period_candles : 1-min candles over a period (a file for each currency_pair for all the days)

        - raw_data_format : dictionary with information about row data files, the required keys vary according to raw_data_type argument, the following are exambles of how the dictionary should be formatted for each type
            - daily_bid_ask: {'date_col':'Gmt Time', 'date_format':'%d.%m.%Y %H:%M:%S.%f', 'ask_col':'Ask', 'bid_col':'Bid'}
            - daily_candles or period_candles: {'date_col':'time', 'date_format':'%Y.%m.%d %H:%M', 'open_col':'open', 'high_col':'high', 'low_col':'low', 'close_col':'close', 'tick_vol_col':'tick_volume'}
        
        - save_logs : boolean flag, if True, the program logs are saved to 'data_dir\\logs\\preprocessing_logs.txt' file.
    Returns:
        - None
    """

    if data_dir is None:
        data_dir = join(getcwd(), 'data')
    if save_logs:
        sys.stdout = open(join(data_dir, 'logs','preprocessing_logs.txt'), 'w')

    #############################################################################################################################
    ##                                                  Daily Bid/Ask Data                                                     ##
    #############################################################################################################################

    if raw_data_type == 'daily_bid_ask':
        # Extract formatting information 
        date_col = raw_data_format['date_col']
        date_format = raw_data_format['date_format']
        ask_col = raw_data_format['ask_col']
        bid_col = raw_data_format['bid_col']

        #############################################################################################################################
        
        if app_type == 'back_tester' or app_type == 'portfolio_optimizer' or app_type == 'all_in_one':
            # Find num_days and time_frames
            num_days = len(listdir(join(data_dir, 'time_frames')))
            tf_list = listdir(join(data_dir, 'time_frames', '0'))
            time_frames = []
            for i in range(1, len(tf_list)+1):
                for tf in tf_list:
                    if tf[1].isalpha():
                        x = int(tf[0])
                    else:
                        x = int(tf[:2])
                    if x == i:
                        time_frames.append(tf)
            for day in range(num_days):
                print('-----------------------------------------------------------------------------------------------------------')
                print('                                             >> Processing Day {} <<'.format(day))
                print('-----------------------------------------------------------------------------------------------------------')

                for i in time_frames:
                    print('\n>> PROCESS MESSAGE >> Processing {} Timeframe ..'.format(i))
                    file_names = [f for f in listdir(join(data_dir, 'raw_data', str(day)))]
                    for file_name in file_names:
                        print('>> PROCESS MESSAGE >>     Processing {} Currency pair ..'.format(file_name[:6]))
                        df = pd.read_csv(join(data_dir, 'raw_data', str(day), file_name))
                        df.index = pd.to_datetime(df[date_col], format=date_format)
                        df = df[[ask_col, bid_col]]
                        df.columns = ['ask', 'bid']
                        df = process_daily_bid_ask(df=df, tf=i)
                        df.to_csv(join(data_dir, 'time_frames', str(day), i, file_name[:6]+'_'+i+'.csv'))
            print('\n>> SYSTEM MESSAGE >> all Days Are Processed Successfully!\n')            
            
            if app_type == 'all_in_one':
                print('>> SYSTEM MESSAGE >> Processing Live App Data!')
                for i in time_frames:
                    print('\n>> PROCESS MESSAGE >> Processing {} Timeframe ..'.format(i))
                    file_names = [f for f in listdir(join(data_dir, 'live_data', 'raw_data'))]
                    for file_name in file_names:
                        print('>> PROCESS MESSAGE >>     Processing {} Currency pair ..'.format(file_name[:6]))
                        df = pd.read_csv(join(data_dir, 'live_data', 'raw_data', file_name))
                        df.index = pd.to_datetime(df[date_col], format=date_format)
                        df = df[[ask_col, bid_col]]
                        df.columns = ['ask', 'bid']
                        df = process_daily_bid_ask(df=df, tf=i)
                        df.to_csv(join(data_dir, 'live_data', 'time_frames', i, file_name[:6]+'_'+i+'.csv'))

        #############################################################################################################################    
        
        elif app_type == 'live_simulator':
            tf_list = listdir(join(data_dir, 'time_frames'))
            time_frames = []
            for i in range(1, len(tf_list)+1):
                for tf in tf_list:
                    if tf[1].isalpha():
                        x = int(tf[0])
                    else:
                        x = int(tf[:2])
                    if x == i:
                        time_frames.append(tf)
            print('>> SYSTEM MESSAGE >> Processing Live App Data!')
            for i in time_frames:
                print('\n>> PROCESS MESSAGE >> Processing {} Timeframe ..'.format(i))
                file_names = [f for f in listdir(join(data_dir, 'raw_data'))]
                for file_name in file_names:
                    print('>> PROCESS MESSAGE >>     Processing {} Currency pair ..'.format(file_name[:6]))
                    df = pd.read_csv(join(data_dir, 'raw_data', file_name))
                    df.index = pd.to_datetime(df[date_col], format=date_format)
                    df = df[[ask_col, bid_col]]
                    df.columns = ['ask', 'bid']
                    df = process_daily_bid_ask(df=df, tf=i)
                    df.to_csv(join(data_dir, 'time_frames', i, file_name[:6]+'_'+i+'.csv'))
                
    #############################################################################################################################
    ##                                                  OHLCV 1min-Candles Data                                                ##
    #############################################################################################################################
    
    elif raw_data_type == 'daily_candles' or raw_data_type == 'period_candles':
        # Extract formatting information 
        date_col = raw_data_format['date_col']
        date_format = raw_data_format['date_format']
        open_col = raw_data_format['open_col']
        close_col = raw_data_format['close_col']
        low_col = raw_data_format['low_col']
        high_col = raw_data_format['high_col']
        tick_vol_col = raw_data_format['tick_vol_col']

        #############################################################################################################################

        if app_type == 'back_tester' or app_type == 'portfolio_optimizer' or app_type == 'all_in_one':
            # Find num_days and time_frames
            num_days = len(listdir(join(data_dir, 'time_frames')))
            tf_list = listdir(join(data_dir, 'time_frames', '0'))
            time_frames = []
            for i in range(1, len(tf_list)+1):
                for tf in tf_list:
                    if tf[1].isalpha():
                        x = int(tf[0])
                    else:
                        x = int(tf[:2])
                    if x == i:
                        time_frames.append(tf)
            for day in range(num_days):
                print('-----------------------------------------------------------------------------------------------------------')
                print('                                             >> Processing Day {} <<'.format(day))
                print('-----------------------------------------------------------------------------------------------------------')

                for i in time_frames:
                    print('\n>> PROCESS MESSAGE >> Processing {} Timeframe ..'.format(i))
                    if raw_data_type == 'daily_candles':
                        file_names = [f for f in listdir(join(data_dir, 'raw_data', str(day)))]
                    else:
                        file_names = [f for f in listdir(join(data_dir, 'raw_data'))]
                    for file_name in file_names:
                        print('>> PROCESS MESSAGE >>     Processing {} Currency pair ..'.format(file_name[:6]))
                        if raw_data_type == 'daily_candles':
                            df = pd.read_csv(join(data_dir, 'raw_data', str(day), file_name))
                        else:
                            df = pd.read_csv(join(data_dir, 'raw_data', file_name))
                        df = pd.DataFrame({'open':df[open_col].values,
                                           'high':df[high_col].values,
                                           'low':df[low_col].values,
                                           'close':df[close_col].values,
                                           'tick_volume':df[tick_vol_col].values}, index=pd.to_datetime(df[date_col], format=date_format))
                        if raw_data_type == 'daily_candles':
                            idx = pd.date_range(df.index.date[0], freq='min', periods=1440)
                            df = df.reindex(idx, method='ffill')
                            df = df.replace(to_replace=np.nan, method='bfill')
                            df = process_ohlc(df=df, tf=i)
                        else:
                            idxs = pd.date_range(df.index.date[0], freq='B', periods=num_days)
                            idx = pd.date_range(idxs[0], freq='min', periods=1440)
                            for date in idxs[1:]:
                                idx = idx.union(pd.date_range(date, freq='min', periods=1440))
                            df = df.reindex(idx, method='ffill')
                            df = df.replace(to_replace=np.nan, method='bfill')
                            df = df.iloc[day*1440:(day+1)*1440]
                            df = process_ohlc(df=df, tf=i)
                        df.to_csv(join(data_dir, 'time_frames', str(day), i, file_name[:6]+'_'+i+'.csv'))
            print('\n>> SYSTEM MESSAGE >> all Days Are Processed Successfully!\n')            
            
            if app_type == 'all_in_one':
                print('>> SYSTEM MESSAGE >> Processing Live App Data!')
                for i in time_frames:
                    print('\n>> PROCESS MESSAGE >> Processing {} Timeframe ..'.format(i))
                    file_names = [f for f in listdir(join(data_dir, 'live_data', 'raw_data'))]
                    for file_name in file_names:
                        print('>> PROCESS MESSAGE >>     Processing {} Currency pair ..'.format(file_name[:6]))
                        df = pd.read_csv(join(data_dir, 'live_data', 'raw_data', file_name))
                        df = pd.DataFrame({'open':df[open_col].values,
                                           'high':df[high_col].values,
                                           'low':df[low_col].values,
                                           'close':df[close_col].values,
                                           'tick_volume':df[tick_vol_col].values}, index=pd.to_datetime(df[date_col], format=date_format))
                        idx = pd.date_range(df.index.date[0], freq='min', periods=1440)
                        df = df.reindex(idx, method='ffill')
                        df = df.replace(to_replace=np.nan, method='bfill')
                        df = process_ohlc(df=df, tf=i)
                        df.to_csv(join(data_dir, 'live_data', 'time_frames', i, file_name[:6]+'_'+i+'.csv'))

        #############################################################################################################################

        elif app_type == 'live_simulator':
            tf_list = listdir(join(data_dir, 'time_frames'))
            time_frames = []
            for i in range(1, len(tf_list)+1):
                for tf in tf_list:
                    if tf[1].isalpha():
                        x = int(tf[0])
                    else:
                        x = int(tf[:2])
                    if x == i:
                        time_frames.append(tf)
            print('>> SYSTEM MESSAGE >> Processing Live App Data!')
            for i in time_frames:
                print('\n>> PROCESS MESSAGE >> Processing {} Timeframe ..'.format(i))
                file_names = [f for f in listdir(join(data_dir, 'raw_data'))]
                for file_name in file_names:
                    print('>> PROCESS MESSAGE >>     Processing {} Currency pair ..'.format(file_name[:6]))
                    df = pd.read_csv(join(data_dir, 'raw_data', file_name))
                    df = pd.DataFrame({'open':df[open_col].values,
                                        'high':df[high_col].values,
                                        'low':df[low_col].values,
                                        'close':df[close_col].values,
                                        'tick_volume':df[tick_vol_col].values}, index=pd.to_datetime(df[date_col], format=date_format))
                    idx = pd.date_range(df.index.date[0], freq='min', periods=1440)
                    df = df.reindex(idx, method='ffill')
                    df = df.replace(to_replace=np.nan, method='bfill')
                    df = process_ohlc(df=df, tf=i)
                    df.to_csv(join(data_dir, 'time_frames', i, file_name[:6]+'_'+i+'.csv'))
    if save_logs:
        sys.stdout.close()
    return

if __name__ == '__main__':
    pass
    
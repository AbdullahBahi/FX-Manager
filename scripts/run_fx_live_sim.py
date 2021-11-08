#!/usr/bin/env python

"""
This script is used for running a live trading simulation with real market prices from MT4 platform.

Usage:
      run_fx_live_sim [options]

Options:
        -h, --help                   : show this help message and exit.

        -v, --version                : show the version of FX-Manager and exit.

        -lrdt, live_raw_data_type    : type of raw data used for portfolio optimization.
                                       Supported Raw Data types: 
                                        - daily_bid_ask  : Bid/Ask ticks in daily seperate files.
                                        (a file for each currency_pair in each day)
                                        - daily_candles  : 1-min candles (OHLCV) in daily seperate files.
                                        (a file for each currency_pair in each day)
                                        - period_candles : 1-min candles (OHLCV) over a period.
                                        (a file for each currency_pair for all the days)

        -om, --optimization_method   : the supported optimization methods are:
                                        - mixed_timeframes: selects the optimal currency pair
                                                            from each available timeframe, then
                                                            selects the optimal equally weighted
                                                            combination of these time frames.
                                        - single_timeframe: selects the optimal time frame from
                                                            the available timeframes, then selects
                                                            the optimal equally weighted combination
                                                            of currency pairs in the selected time frame.

        -obj, --optimization_objective : the supported optimization objectives are:
                                          - min_win_rate   : minimizes the required win rate for
                                                             the portfolio to acheive a positive
                                                             returns.
                                          - min_risk_reward: minimizes the required risk reward
                                                             ratio required for the portfolio to
                                                             acheive a positive returns.

        -eqw, --equally_weighted     : boolean flag, if True, the assets in the constucted
                                       portfolios will be equally weighted.

        -blc, --balance              : initial balance to start simulation with.

        -act, --account_type         : detemines lot size, supported account types are:
                                        - standard: lot size = 100,000
                                        - mini    : lot size = 10,000
                                        - micro   : lot size = 1000
                                        - nano    : lot size = 100

        -acc, --account_currency     : currency of initial balance.

        -lvrg, --leverage            : the leverage provided by the broker (expressed as percentage).

        -vbs, --volume_bounds        : minimum and maximum volume per position, passed as 2 floats 
                                       separated by a space.

        

        -uds, --user_defined_strategy: boolean flag, if True, simulation is done using user-defined
                                       trading strategy which is defined in 'strategy.py' file.

        -tap, --take_all_prices      : boolean flag that controls the frequency of the range index of
                                       'prices' DataFrame which is passed to strategy function.
                                        - If True:
                                       all the prices history since the begining of the day is passed
                                       to the strategy function, the index is a normal range index 
                                       (0, 1, 2, ...). the time difference between every reading is 
                                       determined by the 'sleep_time' argument in the function:
                                       'fxmanager.simulation.historic.run()'.
                                        - If False:
                                       the frequncy of the prices becomes dependant on the time frame
                                       in which we want to generate an order, for examble, if we want
                                       to open a position in 'EURUSD' in the '5min' time frame, the
                                       index will become (0, 5, 10, ..).

        -cp, --construct_portfolio   : boolean flag, if True, the data in  of the previous day stored
                                       in 'data\\live_raw_data' is used to construct a portfolio to be
                                       used for simulation

        -st, --sleep_time            : time between each price update in minutes (float).

        -rf, risk_factor             : percentage of the amount of reinvested cash (float).

        -sz, --sync_zero             : boolean flag, if True, the simulation starts when the seconds
                                       in current time = 0.

        -sl, --save_logs             : boolean flag, if True, the program logs are saved to
                                       'data\\logs\\preprocessing_logs.txt' file.

===========================================================================================
===========================================================================================

Saved Results: 

        - live_porfolio.csv: CSV file for the portfolio used for simulation. saved in
          'data\\stats\\' directory..
        
        - portfolio_orders.csv: CSV file with all the information of all the orders placed 
                                during the simulation. saved in 'data\\stats\\' directory.
"""

doc = __doc__

import argparse
import sys
from os import getcwd
sys.path.append(getcwd())
import json
from fxmanager.basic.account import Account
from fxmanager.basic.util import get_portfolios
from fxmanager.strategies.template import strategy_template
from fxmanager.strategies.naieve_momentum import get_orders
import fxmanager.simulation.live as sim
import fxmanager._metadata as md
import strategy as srtg
from __main__ import __dict__

__dict__.update(md.__dict__)

# Add Optional arguments
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h','--help', default=False, action='store_true')
parser.add_argument('-v','--version', action='version', version=__version__)

parser.add_argument('-lrdt','--live_raw_data_type', type=str, default = 'daily_candles')
parser.add_argument('-om','--optimization_method', type=str, default = 'mixed_timeframes')
parser.add_argument('-obj','--optimization_objective', type=str, default = 'min_win_rate')
parser.add_argument('-eqw','--equally_weighted', default=False, action='store_true')

parser.add_argument('-blc','--balance', type=float, default = 1000.0)
parser.add_argument('-act','--account_type', type=str, default = 'standard')
parser.add_argument('-acc','--account_currency', type=str, default = 'usd')
parser.add_argument('-lvrg','--leverage', type=float, default = 1.0)
parser.add_argument('-vbs','--volume_bounds', type=float, nargs='+', default = [0.01, 8.0])

parser.add_argument('-uds','--user_defined_strategy', default=False, action='store_true')
parser.add_argument('-tap','--take_all_prices', default=False, action='store_true')

parser.add_argument('-cp','--construct_portfolio', default=False, action='store_true')
parser.add_argument('-st','--sleep_time', type=float, default = 1.0)

parser.add_argument('-rf','--risk_factor', type=float, default = 0.98)
parser.add_argument('-sz','--sync_zero', default=False, action='store_true')
parser.add_argument('-sl','--save_logs', default=False, action='store_true')

# Parse arguments
in_args = parser.parse_args()

if in_args.help:
    import sys
    print(doc)
    sys.exit()

# Preprocessing Information (used only if optimization is used [construct_portfolio==True])
with open('raw_data_formats.json') as f:
    raw_data_formats = json.load(f)
if in_args.live_raw_data_type == 'daily_bid_ask':
    raw_data_format = raw_data_formats['daily_bid_ask']
elif in_args.live_raw_data_type == 'daily_candles':
    raw_data_format = raw_data_formats['daily_candles']
elif in_args.live_raw_data_type == 'period_candles':
    raw_data_format = raw_data_formats['period_candles']
else:
    pass 

# Optimization Information (used only if optimization is used [construct_portfolio==True])
optimization_method = in_args.optimization_method
optimization_objective = in_args.optimization_objective
weight_optimization = not in_args.equally_weighted

# Portfolio Information (used only if optimization is NOT used [construct_portfolio==False])
portfolio = srtg.get_portfolios_template()[0]

# Create an account object
acc = Account(balance = in_args.balance,
            account_type = in_args.account_type,
            account_currency = in_args.account_currency,
            leverage = in_args.leverage,
            volume_bounds = in_args.volume_bounds)

# Create a strategy object
if in_args.user_defined_strategy:
        strategy = strategy_template(srtg.template, take_all_prices=in_args.take_all_prices)
        kwargs = srtg.kwargs_template()
else:
        strategy = strategy_template(get_orders, take_all_prices=in_args.take_all_prices)
        kwargs = {'look_back':3}

# Run Simulation
sim.run(account=acc,
        strategy=strategy,
        construct_portfolio=in_args.construct_portfolio,
        portfolio=portfolio,
        weight_optimization=weight_optimization,
        is_preprocessed=in_args.construct_portfolio,
        raw_data_format=raw_data_format,
        optimization_method=in_args.optimization_method,
        optimization_objective=in_args.optimization_objective,
        sleep_time=in_args.sleep_time, ## In Minutes
        risk_factor=in_args.risk_factor, ## percentage of money to be invested from account balance during simulation
        sync_zero=in_args.sync_zero,
        save_logs=in_args.save_logs,
        **kwargs) ## Multiple of the timeframe (i.e. if an order to be placed in 10 min tf, look back would be 30 minutes with check every 10min)
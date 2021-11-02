#!/usr/bin/env python

"""
This script is used for running a historical trading simulation with historical prices.

Usage:
      run_fx_hist_sim [options]

Options:
        -h, --help                   : show this help message and exit.

        -v, --version                : show the version of FX-Manager and exit.

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

        -rf, risk_factor             : percentage of the amount of reinvested cash.

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

        -nd, --num_days              : total number of work days in the dataset.

        -ops, --optimized_portfolios : boolean flag, if True, the simulation uses the optimized portfolios
                                       saved in 'data\\stats\\Optimizer_test_results.csv'. this option
                                       should only be used after running 'optimizer_test.py' script on
                                       the same historical data used for simulation.

        -usp, --use_single_porfolio  : boolean flag, used if 'optimized_portfolios' is False, set to True 
                                       if you want to use the same portfolio for all the days, if False,
                                       'portfolios' dictionary is used instead.

        -sl, --save_logs             : boolean flag, if True, the program logs are saved to
                                       'data\\logs\\preprocessing_logs.txt' file.

===========================================================================================
===========================================================================================

Saved Results: 
        
        - portfolio_orders.csv: CSV file with all the information of all the orders placed 
                                during the simulation. saved in 'data\\stats\\' directory.
"""

doc = __doc__

import argparse
import sys
from os import getcwd
sys.path.append(getcwd())
from fxmanager.basic.account import Account
from fxmanager.basic.util import get_portfolios
from fxmanager.strategies.template import strategy_template
from fxmanager.strategies.naieve_momentum import get_orders
import fxmanager.simulation.historic as sim
import fxmanager._metadata as md
import strategy as srtg
from __main__ import __dict__

__dict__.update(md.__dict__)

# Add Optional arguments
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h','--help', default=False, action='store_true')
parser.add_argument('-v','--version', action='version', version=__version__)
parser.add_argument('-blc','--balance', type=float, default = 1000.0)
parser.add_argument('-act','--account_type', type=str, default = 'standard')
parser.add_argument('-acc','--account_currency', type=str, default = 'usd')
parser.add_argument('-lvrg','--leverage', type=float, default = 1.0)
parser.add_argument('-vbs','--volume_bounds', type=float, nargs='+', default = [0.01, 8.0])
parser.add_argument('-rf','--risk_factor', type=float, default = 0.98)
parser.add_argument('-uds','--user_defined_strategy', default=False, action='store_true')
parser.add_argument('-tap','--take_all_prices', default=False, action='store_true')
parser.add_argument('-nd','--num_days', type=int, default = 2)
parser.add_argument('-ops','--optimized_portfolios', default=False, action='store_true')
parser.add_argument('-usp','--use_single_porfolio', default=False, action='store_true')
parser.add_argument('-sl','--save_logs', default=False, action='store_true')

# Parse arguments
in_args = parser.parse_args()

if in_args.help:
    import sys
    print(doc)
    sys.exit()

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

# Get Portfolios
portfolios = get_portfolios(num_days=in_args.num_days,
                            single_portfolio=srtg.get_portfolios_template()[0],
                            portfolios=srtg.get_portfolios_template(),
                            optimized_portfolios=in_args.optimized_portfolios,
                            use_single_porfolio=in_args.use_single_porfolio)

sim.run(account = acc,
        strategy = strategy,
        portfolios = portfolios,
        risk_factor = in_args.risk_factor,
        save_logs = in_args.save_logs,
        **kwargs)


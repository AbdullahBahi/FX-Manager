#!/usr/bin/env python

"""
This script is used for pre-processing raw market prices data to be compaitable with FX-Manager.

This script should be used after running 'setup.py' script. data is organized in the following
structure:
    >> 'data\\timeframes\\':
        >> '0\\':
            >> '1min\\':
                >> 'currency_pair_processed_data_file.csv'
                >> 'other_currency_pair_processed_data_file.csv'
                >> ...
            >> '2min\\':
                >> 'currency_pair_processed_data_file.csv'
                >> 'other_currency_pair_processed_data_file.csv'
                >> ...
            >> ...
        >> '1\\':
            >> ...
        >> ...

Usage:
      fx_pp [options]

Options:
    -h, --help                 : show this help message and exit.
    
    -v, --version              : show the version of FX-Manager and exit.
    
    -at, --app_type            : Supported App types: 
                                    - back_tester          : if you want to test trading strategies 
                                                             histoical data on FX-Manager virtual account.
                                    - portfolio_optimizer  : if you want to asses different portfolio optimization
                                                             methods and objectives using histoical data.
                                    - live_simulator       : if you want to test trading strategies in real time
                                                             using MT4 Live data on FX-Manager virtual account.
                                    - all_in_one           : if you want to use all the previous features.
    
    -rdt, --raw_data_type      : Supported Raw Data types: 
                                    - daily_bid_ask  : Bid/Ask ticks in daily seperate files.
                                      (a file for each currency_pair in each day)
                                    - daily_candles  : 1-min candles (OHLCV) in daily seperate files.
                                      (a file for each currency_pair in each day)
                                    - period_candles : 1-min candles (OHLCV) over a period.
                                      (a file for each currency_pair for all the days)
    
    -sl, --save_logs           : boolean flag, if True, the program logs are saved to
                                 'data\\logs\\preprocessing_logs.txt' file
"""

doc = __doc__

from os import getcwd
from os.path import join
import json
import argparse
from fxmanager.basic.util import preprocess
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

# Add Optional arguments
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h','--help', default=False, action='store_true')
parser.add_argument('-v','--version', action='version', version=__version__)
parser.add_argument('-at','--app_type', type=str, default = 'all_in_one')
parser.add_argument('-rdt','--raw_data_type', type=str, default = 'daily_candles')
parser.add_argument('-sl','--save_logs', default=False, action='store_true')

# Parse arguments
in_args = parser.parse_args()

if in_args.help:
    import sys
    print(doc)
    sys.exit()
    
with open('raw_data_formats.json') as f:
    raw_data_formats = json.load(f)

if in_args.raw_data_type == 'daily_bid_ask':
    raw_data_format = raw_data_formats['daily_bid_ask']
elif in_args.raw_data_type == 'daily_candles':
    raw_data_format = raw_data_formats['daily_candles']
elif in_args.raw_data_type == 'period_candles':
    raw_data_format = raw_data_formats['period_candles']
else:
    pass 

preprocess(app_type = in_args.app_type,
            raw_data_type = in_args.raw_data_type,
            raw_data_format = raw_data_format,
            save_logs = in_args.save_logs)


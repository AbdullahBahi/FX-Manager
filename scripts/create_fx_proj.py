#!/usr/bin/env python

"""
This script is used for setting up a new FX-Manager project.

Usage:
      create_fx_proj [options]

Options:
      -h, --help                : show this help message and exit.
      
      -v, --version             : show the version of FX-Manager and exit.

      -at, --app_type           : Supported App types: 
                                    - back_tester          : if you want to test trading strategies using histoical data
                                                             on FX-Manager virtual account.
                                    - portfolio_optimizer  : if you want to asses different portfolio optimization methods
                                                             and objectives using histoical data.
                                    - live_simulator       : if you want to test trading strategies in real time using MT4
                                                             Live data on FX-Manager virtual account.
                                    - all_in_one           : if you want to use all the previous features.

      -rdd, --raw_data_dir       : path to the directory where raw historical data files exist.
                                   path could be relative or full.
      
      -rdt, --raw_data_type      : Supported Raw Data types: 
                                    - daily_bid_ask  : Bid/Ask ticks in daily seperate files.
                                      (a file for each currency_pair in each day)
                                    - daily_candles  : 1-min candles in daily seperate files.
                                      (a file for each currency_pair in each day)
                                    - period_candles : 1-min candles over a period.
                                      (a file for each currency_pair for all the days)
      
      -lrdd, --live_raw_data_dir : path to the directory where raw historical data files used for
                                   live simulation exist. path could be relative or full.
      
      -fnf, --file_name_format   : string of white spaces with the same length as raw data file names.
                                   Givin that each file name has information about date and currency pair
                                   symbol, the white spaces in the same location as these information are
                                   replaced as follows:
                                    - day, month and year in the date are replaced with (dd), (mm), (yyyy) respectively.
                                    - currency pair symbol is replaced with (cccccc).
                                    Example:
                                    if the file name is "AUDUSD_Ticks_02.08.2021-02.08.2021.csv"
                                    then the -fnf is:
                                                        "cccccc       dd mm yyyy               "
      
      -nd, --num_days           : total number of work days in the dataset.
      -ncp, --num_currency_pairs : number of currency pairs in the dataset.
      -ntf, --num_time_frames    : number of timeframes in the dataset.
"""

doc = __doc__ 

import argparse
from fxmanager.basic.util import setup
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

# Add Optional arguments
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h','--help', default=False, action='store_true')
parser.add_argument('-v','--version', action='version', version=__version__)
parser.add_argument('-at','--app_type', type=str, default = 'all_in_one')
parser.add_argument('-rdd','--raw_data_dir', type=str, default = 'raw_data')
parser.add_argument('-rdt','--raw_data_type', type=str, default = 'daily_candles')
parser.add_argument('-lrdd','--live_raw_data_dir', type=str, default = 'live_raw_data')    
parser.add_argument('-fnf','--file_name_format', type=str, default = 'cccccc yyyy mm dd    ')
parser.add_argument('-nd','--num_days', type=int, default = 2)
parser.add_argument('-ncp','--num_currency_pairs', type=int, default = 1)
parser.add_argument('-ntf','--num_time_frames', type=int, default = 10)

# Parse arguments
in_args = parser.parse_args()

if in_args.help:
  import sys
  print(doc)
  sys.exit()

# File Name Formats:
#     - daily_bid_ask  : 'cccccc       dd mm yyyy               '
#     - daily_candles  : 'cccccc yyyy mm dd    '
#     - period_candles : 'cccccc yyyy mm dd               '

setup(app_type = in_args.app_type,
        raw_data_dir = in_args.raw_data_dir,
        live_raw_data_dir = in_args.live_raw_data_dir,
        raw_data_type = in_args.raw_data_type,
        file_name_format = in_args.file_name_format,
        num_days = in_args.num_days,
        num_cps = in_args.num_currency_pairs,
        num_tfs = in_args.num_time_frames)
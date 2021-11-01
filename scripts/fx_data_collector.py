#!/usr/bin/env python

"""
This script is used for collecting data from MT4 history center.

To use this script you must download the data of the required
currency pair from MT4 history center first, this guild shows
the steps ti do this: 
https://www.metatrader4.com/en/trading-platform/help/service/history_center

Usage:
      fx_data_collector [options]

Options:
      -h, --help            : show this help message and exit.
      
      -v, --version         : show the version of FX-Manager and exit.

      -rdt, --raw_data_type : Supported Raw Data types:
                                    - daily_candles  : 1-min candles (OHLCV) in daily seperate files.
                                      (a file for each currency_pair for each day)
                                    - period_candles : 1-min candles (OHLCV) over a period.
                                      (a single file for each currency_pair)
      
      -cps, --currency_pairs: list of symbols of the desired currency pairs of which data is collected.
                              symbolS are separated by a white blanc character (space).

      -s, --start           : start date of the period of which data is collected. must be passed in the
                              form YYYY_mm_dd.

      -e, --end             : end date of the period of which data is collected. must be passed in the
                              form YYYY_mm_dd.
      
      -st, save_to          : path to the directory where data is saved, could be absolut or relative. 
"""

doc = __doc__

from os import getcwd
import argparse
import pandas as pd
from fxmanager.dwx.rates_historic import rates_historic as rh
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

# Add Optional arguments
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h','--help', default=False, action='store_true')
parser.add_argument('-v','--version', action='version', version=__version__)
parser.add_argument('-rdt','--raw_data_type', type=str, default = 'daily_candles')
parser.add_argument('-cps','--currency_pairs', type=str, nargs='+', default = ['EURUSD'])
parser.add_argument('-s','--start', type=str, default = '2021_09_20')
parser.add_argument('-e','--end', type=str, default = '2021_09_21')
parser.add_argument('-st','--save_to', type=str, default = getcwd())

# Parse arguments
in_args = parser.parse_args()

if in_args.help:
    import sys
    print(doc)
    sys.exit()

cps = [x.upper() for x in in_args.currency_pairs]

start_date = pd.to_datetime(in_args.start, format='%Y_%m_%d')
end_date = pd.to_datetime(in_args.end, format='%Y_%m_%d')
dates = pd.date_range(start=start_date, end=end_date)

# Create a data collector object
dc = rh()

for cp in cps:
    if in_args.raw_data_type == 'daily_candles':
        for date in dates:
            # remove weekends
            if date.weekday() == 5 or date.weekday() == 6:
                continue
            dc.get_daily_candles(save_to = in_args.save_to, currency_pair=cp, date='.'.join(str(date.date()).split('-')))

    elif in_args.raw_data_type == 'period_candles':
        # remove weekends
        dates = dates[dates.weekday != 5] & dates[dates.weekday != 6]
        dc.get_period_candles(save_to = in_args.save_to, currency_pair=cp, start='.'.join(str(dates[0].date()).split('-')), end='.'.join(str(dates[-1].date()).split('-')))
#!/usr/bin/env python

"""
This script runs a portfolio optimization test using historical data.

Assuming the dataset has N working days sorted in folders (0, 1, 2, ...)
in 'data\\raw_data\\' directory, this test uses the data of each single
day (n) to construct an optimized portfolio of a compination of currency
pairs, then uses the constructed portfolio to calculate the expected 
returns if this portfolio is used for trading in the next day (n+1).

a portfolio consists of one or more assets where an asset in this context
refers to a currency pair being traded in a specefic time frame. for example:
if the currency pair 'EURUSD' is being traded in two different time frames,
5 and 10 minutes (a new position is opened every 5 or 10 minutes), in this case,
the 'EURUSD_5min' and 'EURUSD_10min' are two different assets.

Usage:
      run_fx_opt_test [options]

Options:
      -h, --help                     : show this help message and exit.
      
      -v, --version                  : show the version of FX-Manager and exit.
      
      -om, --optimization_method     : the supported optimization methods are:
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

      -spd, --scenarios_per_day      : number of scenarios over which the expected return
                                       is averaged every day (must be integer)

      -rr, --risk_rewards            : list of risk-reward ratios for which the expected
                                       return is calculated. (must be floats in quote marks
                                       and separated by spaces)
      
      -lvrg, --leverage              : leverage used for calculating expected returns 
                                       (must be float in quote marks)
      
      -eqw, --equally_weighted       : boolean flag, if True, the assets in the constucted
                                       portfolios will be equally weighted.

      -sap, --single_asset_portfolio : boolean flag, if True, the constucted portfolios will
                                       consist of a single asset.

      -sp, --save_plots              : boolean flag, if True, the program will save result 
                                       plots to 'data\\visualizations\\' directory.
                                       
      -sl, --save_logs               : boolean flag, if True, the program logs are saved to
                                       'data\\logs\\equally_weighted_optimizer_logs.txt' file.

===========================================================================================
===========================================================================================

Saved Results: 
    ** test results are saved to 'data\\visualizations' for plots and
       'data\\stats' for csv files.
        
    - Optimizer_Test_Win_Probs_&_Expexted_Rets_vs_Offsets.png :
        image with 2 sub-plots sharing the X-axis for the offsets, and Y axis for win 
        probabilites and average expected returns. Offsets are linearly separated
        floats added to the 'min_win_rate' argument, starting from (0.01, 0.02, ...),
        the value of 'min_win_rate' is incremented until the win probabilty becomes
        greater than or equal to 1. the plot might also contain several lines per plot,
        each line represents calculations a single risk-reward ratio.
    
    - Optimizer_Test_Required_Win_Rates.png : 
        image with a plot of constructed portfolios win rates on the Y-axis vs days on the X-axis.
    
    - Optimizer_Test_Risk _Reward_Ratios.png : 
        image with a plot of constructed portfolios risk rewards on the Y-axis vs days on the X-axis.

    - Optimizer_Test_portfolios.csv : 
        CSV file with the constructed portfolios for every day. the index starts from 1 because every
        row represents the portfolio created using data from the day before so day 0 does not count.

    - Optimizer_Test_win_probs.csv :
        CSV file with the data frame used for plotting the first sub-plot in
        'Optimizer_Test_Win_Probs_&_Expexted_Rets_vs_Offsets.png'
    
    - Optimizer_Test_expexted_returns.csv :
        CSV file with the data frame used for plotting the second sub-plot in
        'Optimizer_Test_Win_Probs_&_Expexted_Rets_vs_Offsets.png'
"""

doc = __doc__

import argparse
import sys
if '--equally_weighted' in sys.argv or '-eqw' in sys.argv:
    import fxmanager.optimization.eqw_optimization_test as optim
else:
    import fxmanager.optimization.w_optimization_test as optim

import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

# Add Optional arguments
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h','--help', default=False, action='store_true')
parser.add_argument('-v','--version', action='version', version=__version__)
parser.add_argument('-om','--optimization_method', type=str, default = 'mixed_timeframes')
parser.add_argument('-obj','--optimization_objective', type=str, default = 'min_win_rate')
parser.add_argument('-spd','--scenarios_per_day', type=int, default = 100)
parser.add_argument('-rr','--risk_rewards', type=float, nargs='+', default = [0.8, 0.9, 1, 1.1, 1.2])
parser.add_argument('-lvrg','--leverage', type=float, default = 1.0)
parser.add_argument('-eqw','--equally_weighted', default=False, action='store_true')
parser.add_argument('-sap','--single_asset_portfolio', default=False, action='store_true')
parser.add_argument('-sp','--save_plots', default=False, action='store_true')
parser.add_argument('-sl','--save_logs', default=False, action='store_true')

# Parse arguments
in_args = parser.parse_args()

if in_args.help:
    import sys
    print(doc)
    sys.exit()
    
## Run the test
optim.run_test(optimization_method = in_args.optimization_method,
                optimization_objective = in_args.optimization_objective,
                scenarios_per_day = in_args.scenarios_per_day,
                risk_rewards = in_args.risk_rewards,
                leverage = in_args.leverage,
                test_run = in_args.single_asset_portfolio,
                save_plots = in_args.save_plots,
                save_logs = in_args.save_logs)
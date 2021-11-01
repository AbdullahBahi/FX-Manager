#!/usr/bin/env python

"""
This module contains a function that rans a weighted optimization test on historical data.

Functions:
    - run_test(): Runs an optimization test on historical data given an 'optimization_method' and 'optimization_objective'.
"""

import sys
from os import getcwd, listdir
from os.path import join
from time import sleep
from itertools import combinations
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import fxmanager.optimization.weight_optimizer as optim
import fxmanager.basic.util as util
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

def run_test(data_dir=None, optimization_method="", optimization_objective="", scenarios_per_day=100, risk_rewards=[], leverage=0.01, test_run=False, save_plots=False, save_logs=False):
    """
    Runs an optimization test given an 'optimization_method' and 'optimization_objective'.
    
    The test uses preprocessed historical data to construct a portfolio using data from day (n) and then we use this portfolio to calculate
    average expected returns in day (n+1). The expected returns are calculated for every single element in 'risk_rewards' list and then
    averaged over 'scenarios_per_day' every day.

    Args:
        - data_dir              : string with the directory or full path to the directory in which application data is kept. If the setup() function is used to create the recommended project structure, the default None value should be used.
        
        - optimization_method   : string with optimization method to be used. The supported optimization methods are:
            - mixed_timeframes : selects the optimal currency pair from each available timeframe, then selects the optimal combination of these time frames and the optimal weight for each time frame.
            - single_timeframe : selects the optimal time frame from the available timeframes, then selects the optimal combination of currency pairs in the selected time frame and the optimal weight for each currency pair.
        
        - optimization_objective: string with optimization objective to be used. The supported optimization objectives are:
            - min_win_rate    : minimizes the required win rate for the portfolio to acheive a positive returns.
            - min_risk_reward : minimizes the required risk reward ratio required for the portfolio to acheive a positive returns.

        - scenarios_per_day     : integer indicating the number of scenarios over which the expected return is averaged every day. 
        - risk_rewards          : list of integers. the average expected return is calculated for every integer in this list every day.
        - leverage              : float indicating the leverage. if no leverage is used set to 1.
        - test_run              : boolean flag used for testing purposes. If true, the constructed portfolios will consist of only one asset.
        - save_plots            : boolean flag. If True, the program will save result plots to 'data_dir\\visualizations\\' directory.
        - save_logs             : boolean flag. If True, the program will save result plots to 'data_dir\\logs\\equally_weighted_optimizer_logs.txt' file.
    Returns:
        - None
    
    Saved Results: test results are saved to 'data_dir\\visualizations' for plots and 'data_dir\\stats' for csv files.
        
        - Optimizer_Test_Win_Probs_&_Expexted_Rets_vs_Offsets.png : image with 2 sub-plots sharing the X-axis for the offsets, and Y axis for win probabilites and average expected returns.  
          Offsets are linearly separated floats added to the 'min_win_rate' argument, starting from (0.01, 0.02, ...), the value of 'min_win_rate' is incremented until the win probabilty becomes greater than or equal to 1.  
          The plot might also contain several lines per plot, each line represents calculations a single risk-reward ratio.
        
        - Optimizer_Test_Required_Win_Rates.png : image with a plot of constructed portfolios win rates on the Y-axis vs days on the X-axis.
        
        - Optimizer_Test_Risk _Reward_Ratios.png : image with a plot of constructed portfolios risk rewards on the Y-axis vs days on the X-axis.

        - Optimizer_Test_portfolios.csv : csv file with the constructed portfolios for every day. the index starts from 1 because every row represents the portfolio created using data from the day before and tested on the current day.

        - Optimizer_Test_win_probs.csv : csv file with the data frame used for plotting the first sub-plot in 'Optimizer_Test_Win_Probs_&_Expexted_Rets_vs_Offsets.png'
        
        - Optimizer_Test_expexted_returns.csv : csv file with the data frame used for plotting the second sub-plot in 'Optimizer_Test_Win_Probs_&_Expexted_Rets_vs_Offsets.png'
    """

    if data_dir is None:
        data_dir = join(getcwd(), 'data')

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
    currency_pairs = [x[:6] for x in listdir(join(data_dir, 'time_frames', '0', '1min'))]

    # Initialize data placeholders to empty dataframes
    offset_win_probs = pd.DataFrame()
    offset_er = pd.DataFrame()
    portfolios = pd.DataFrame()

    if save_logs:
        sys.stdout = open(join(data_dir, 'logs','weighted_optimizer_logs.txt'), 'w')

    for d in range(num_days-1):
        print('-----------------------------------------------------------------------------------------------------------')
        print('-----------------------------------------------------------------------------------------------------------')
        print('                                             >> Processing Day {} <<'.format(d+1))
        print('-----------------------------------------------------------------------------------------------------------')
        print('-----------------------------------------------------------------------------------------------------------')
        ## STAGE 1 : Load best and worst returns
        print('\n>> SYSTEM MESSAGE >> STAGE 1: Loading Data ..\n')
        sleep(1)
        best_rets_df, wrst_rets_df = util.get_avg_rets(day=d, data_dir=data_dir, time_frames=time_frames, currency_pairs=currency_pairs)
        best_rets_df.index, wrst_rets_df.index = range(best_rets_df.shape[0]), range(best_rets_df.shape[0]) 

        ## STAGE 2 : Start Optimizing the portfolio
        print('>> SYSTEM MESSAGE >> Data Loaded Successfully!\n')
        print('>> SYSTEM MESSAGE >> STAGE 2: Optimizing Portfolio Parameters ..')
        
        optimized_portfolio_idxs, optimized_portfolio_tfs, optimized_portfolio_weights, \
        optimized_n, optimized_W_R, optimized_R_R = optim.optimize(best_rets_df,
                                                                    wrst_rets_df,
                                                                    data_dir=data_dir,
                                                                    method=optimization_method,
                                                                    objective=optimization_objective,
                                                                    test_run=test_run)
        optimized_portfolio_cps = [currency_pairs[x] for x in optimized_portfolio_idxs]

        ## STAGE 3 : Calculate the returns in the following day using the optimized portfolio
        print('\n>> SYSTEM MESSAGE >> Portfilio Construction is complete! ..\n')
        sleep(1)
        print('>> SYSTEM MESSAGE >> STAGE 3: Calculating Returns Using the Constructed Portfolio .. ')
        sleep(1)
        
        for rr in risk_rewards:
            win_probability = 0
            offset_W_R = 0
            offset_win_probs_day = pd.DataFrame()
            offset_er_day = pd.DataFrame()
            while win_probability < 1:
                er, win_probability = util.expected_return(day = d+1,
                                                            data_dir=data_dir,
                                                            time_frames = optimized_portfolio_tfs,
                                                            currency_pairs = optimized_portfolio_cps,
                                                            weights=optimized_portfolio_weights,
                                                            leverage=leverage,
                                                            win_rate = optimized_W_R + offset_W_R,
                                                            risk_reward = rr,
                                                            n_scenarios = scenarios_per_day)
                offset_win_probs_day[str(round(offset_W_R,2))] = [win_probability]
                offset_er_day[str(round(offset_W_R,2))] = [er]
                offset_W_R += 0.01
            offset_win_probs_day.index = [rr]
            offset_er_day.index = [rr]
            offset_win_probs = offset_win_probs.append(offset_win_probs_day, sort=True)
            offset_er = offset_er.append(offset_er_day, sort=True)

        ## STAGE 4 : Print the results
        print('\n>> SYSTEM MESSAGE >> Returns are Calculated Successfully!\n')
        print('>> SYSTEM MESSAGE >> STAGE 4: Printing Day results ..\n')
        sleep(1)
        print(f'\n>> PROCESS MESSAGE >>  Day {d+1} Results: ')
        print(f'>> PROCESS MESSAGE >> Number of Assets Used in the Portfolio                : {optimized_n} Assets')
        print(f'>> PROCESS MESSAGE >> Portfolio Currency Pairs                              : {optimized_portfolio_cps}')
        print(f'>> PROCESS MESSAGE >> Portfolio Time Frames                                 : {optimized_portfolio_tfs}')
        print(f'>> PROCESS MESSAGE >> Portfolio Weights                                     : {optimized_portfolio_weights}')
        print(f'>> PROCESS MESSAGE >> Lowest Win Rate Required to get profit                : {round(optimized_W_R*100, 2)}%')
        print(f'>> PROCESS MESSAGE >> Portfolio Risk-Reward ratio                           : {round(optimized_R_R*100, 2)}%')
        print(f'>> PROCESS MESSAGE >> Win Probability at {round(offset_W_R*100,2)}% Extra Win Rate                : {round(win_probability*100, 2)}%')
        print(f'>> PROCESS MESSAGE >> Average Expexted Return across {scenarios_per_day} scenarios          : {round(er*100, 2)}%')

        portfolios[d+1] = pd.Series({'optimized_W_R' : optimized_W_R,
                                     'optimized_R_R' : optimized_R_R,
                                     'optimized_n'   : optimized_n,
                                     'currency_pairs': optimized_portfolio_cps,
                                     'time_frames'    : optimized_portfolio_tfs,
                                     'weights': optimized_portfolio_weights
                                    })

    ## STAGE 5 : Save Results & Stats
    print('\n>> SYSTEM MESSAGE >> No More Days are Left! Go get More Data!\n')
    sleep(1)
    print('>> SYSTEM MESSAGE >> STAGE 4: Saving Results and Portfolios Summary..\n')
    sleep(1)

    if save_logs:
        sys.stdout.close()

    if save_plots:
        # Get average expected returns and win probs over all days for each risk reward value
        AVG_er = pd.DataFrame()
        AVG_win_probs = pd.DataFrame()
        for rr in risk_rewards:
            AVG_er[rr] = offset_er.loc[rr].mean(axis=0)
            AVG_win_probs[rr] = offset_win_probs.loc[rr].mean(axis=0)

        AVG_er.index.name, AVG_win_probs.index.name = 'Win Rate Offsets', 'Win Rate Offsets'

        # Create a figure with 2 subplots
        fig1, (ax1,ax2) = plt.subplots(2, 1, figsize = [10, 15])

        # Plot the Win Probabilites vs Win Rate Offsets in the upper subplot
        AVG_win_probs.plot(ax=ax1, grid=True, sharex=True, title='Win Probabilites & Expexted Returns vs Win Rate Offsets', legend=True)
        ax1.set_ylim(0,1)
        ax1.set_ylabel('Win Probabilites')
        ax1.legend(title="Risk Reward Ratios", fancybox=True)

        # Plot the Expexted Returns vs Win Rate Offsets in the lower subplot
        AVG_er.plot(ax=ax2, grid=True, sharex=True, legend=True)
        ax2.set_ylabel('Expexted Returns')
        ax2.legend(title="Risk Reward Ratios", fancybox=True)

        # Save the figure as png image
        fig1.savefig(join(data_dir,'visualizations','Optimizer_Test_Win_Probs_&_Expexted_Rets_vs_Offsets.png'))

        # Create a new figure
        fig2 = plt.figure(figsize = [15, 10])
        ax3 = plt.gca()

        # Plot the optimized win rates of all portfolios (x-axis is the days, one portfolio for each day)
        portfolios = portfolios.transpose()
        portfolios['optimized_W_R'].plot(ax=ax3, grid=True, title='Minimum Required Win Rates', label='Win Rates')
        ax3.axhline(y=portfolios['optimized_W_R'].mean(), color='r', linestyle='--', label='Average Win Rate')
        ax3.set_xlim(0,21)
        ax3.legend()
        ax3.set_ylabel('Win Rates')

        # Save the figure as png image
        fig2.savefig(join(data_dir,'visualizations','Optimizer_Test_Required_Win_Rates.png'))

        # Create a new figure
        fig3 = plt.figure(figsize = [15, 10])
        ax4 = plt.gca()

        # Plot the optimized risk reward ratios of all portfolios (x-axis is the days, one portfolio for each day)
        portfolios['optimized_R_R'].plot(ax=ax4, grid=True, title='Risk-Reward Ratios', label='Risk-Reward Ratios')
        ax4.axhline(y=portfolios['optimized_R_R'].mean(), color='r', linestyle='--', label='Average Risk-Reward Ratio')
        ax4.set_xlim(0,21)
        ax4.legend()
        ax4.set_ylabel('Risk-Reward ratios')

        # Save the figure as png image
        fig3.savefig(join(data_dir,'visualizations','Optimizer_Test_Risk _Reward_Ratios.png'))

    # portfolios = portfolios.transpose()
    portfolios.index.name, offset_win_probs.index.name, offset_er.index.name = 'days','days' ,'days'
    offset_er.index = np.array([np.arange(1, num_days)]*len(risk_rewards)).T.flatten()
    offset_win_probs.index = np.array([np.arange(1, num_days)]*len(risk_rewards)).T.flatten()
    portfolios.to_csv(join(data_dir, 'stats', 'Optimizer_Test_portfolios.csv'))
    offset_win_probs.to_csv(join(data_dir, 'stats', 'Optimizer_Test_win_probs.csv'))
    offset_er.to_csv(join(data_dir, 'stats', 'Optimizer_Test_expexted_returns.csv'))


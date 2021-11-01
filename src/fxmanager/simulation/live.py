#!/usr/bin/env python

"""
This module contains helper functions used internally in this module and a public function to run live simulation with live price feed from MT4.

Public Functions:
    - run(): starts trading simulation with live prices from MT4 EA.
"""

import sys
from os import listdir, getcwd
from os.path import join
from time import sleep, time, asctime, localtime
import pandas as pd 
from fxmanager.basic.util import preprocess, get_avg_rets
from fxmanager.dwx.prices_subscriptions import prices_subscriptions as ps
import fxmanager.optimization.eq_weight_optimizer as optim
import fxmanager.optimization.weight_optimizer as optim_w
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

##########################################################################################################################
##                                                 Helper Functions
##########################################################################################################################

def optimize_portfolio(data_dir, raw_data_format, optimization_method, optimization_objective, weight_optimization=False, is_preprocessed=True):
    """
    helper function to 'fxmanager.simulation.live.run()' function. Does portfolio optimization using data from previous day. The constructed portfolio is used for live simulation.

    Returns:
        - portfolio     : dictionary with keys ('currency_pairs', 'time_frames', 'weights', 'optimized_n', 'optimized_W_R', 'optimized_R_R')
        - currency_pairs: list with portfolio currency pairs.
        - time_frames   : list with portfolio timeframes.
        - weights       : list with portfolio weights.
    """

    # Extract the time frames and currency pairs lists
    time_frames = listdir(join(data_dir, 'time_frames', '0'))
    time_frames.append(time_frames[0])
    time_frames = time_frames[1:]
    currency_pairs = [x[:6] for x in listdir(join(data_dir, 'time_frames', '0', '1min'))]
    
    ## STAGE 1: Preprocessing Data of Previous 24 Hours
    if not is_preprocessed:
        print('\n>> SYSTEM MESSAGE >> STAGE 1: Preprocessing Data of Previous 24 Hours ..\n')
        preprocess(data_dir=data_dir,
                    raw_data_format=raw_data_format,
                    is_live_data=True,
                    save_logs=False)
        print('>> SYSTEM MESSAGE >> Data Processed Successfully!\n')
    else:
        print('\n>> SYSTEM MESSAGE >> STAGE 1: Data of Previous 24 Hours Is Already Preprocessed! Skipping Stage 1 ..\n')
    
    ## STAGE 2: Optimizing Portfolio Parameters
    print('>> SYSTEM MESSAGE >> STAGE 2: Optimizing Portfolio Parameters ..\n')
    # First load best and worst returns
    best_rets_df, wrst_rets_df = get_avg_rets(day=0, data_dir=join(data_dir,'live_data'), time_frames=time_frames, currency_pairs=currency_pairs)
    best_rets_df.index, wrst_rets_df.index = range(best_rets_df.shape[0]), range(best_rets_df.shape[0]) 

    # Now start optimizing the portfolio
    if weight_optimization:
        optimized_portfolio_idxs, optimized_portfolio_tfs, optimized_portfolio_weights, \
        optimized_n, optimized_W_R, optimized_R_R = optim_w.optimize(best_rets_df,
                                                                    wrst_rets_df,
                                                                    method=optimization_method,
                                                                    objective=optimization_objective,
                                                                    test_run=True)
    else:
        optimized_portfolio_idxs, optimized_portfolio_tfs, optimized_portfolio_weights, \
        optimized_n, optimized_W_R, optimized_R_R = optim.optimize(best_rets_df,
                                                                    wrst_rets_df,
                                                                    method=optimization_method,
                                                                    objective=optimization_objective,
                                                                    test_run=True)
    optimized_portfolio_cps = [currency_pairs[x] for x in optimized_portfolio_idxs]
    
    portfolio = {'currency_pairs':optimized_portfolio_cps,
                'time_frames':optimized_portfolio_tfs,
                'weights':optimized_portfolio_weights,
                'optimized_n':optimized_n, 'optimized_W_R':optimized_W_R, 'optimized_R_R':optimized_R_R}
    
    currency_pairs = portfolio['currency_pairs']
    time_frames = portfolio['time_frames']
    weights = portfolio['weights']

    print('>> SYSTEM MESSAGE >> Portfilio Construction is complete! ..\n')

    return portfolio, currency_pairs, time_frames, weights

def get_price(currency_pairs, price_feed, sleep_time):
    """
    helper function to 'fxmanager.simulation.live.run()' function. gets the current prices of portfolio assets from price feed.

    Returns:
        - price_every_iter_df: pandas dataframe with length = 1 and (4* number of currency pairs) columns. Each asset has 4 columns as follows, (000000_bid_open, 000000_ask_open, 000000_bid_close, 000000_ask_close) where 000000 is replaced with currency pair symbol.
    """

    t = time()
    price_every_iter = {}
    
    # get open prices
    for cp in currency_pairs:
        prices = price_feed._recent_prices[cp]
        price_every_iter[cp+'_bid_open'] = min(prices)
        price_every_iter[cp+'_ask_open'] = max(prices)

    # get close prices
    while (time()-t) < (sleep_time*60):
        for cp in currency_pairs:
            prices = price_feed._recent_prices[cp]
            price_every_iter[cp+'_bid_close'] = min(prices)
            price_every_iter[cp+'_ask_close'] = max(prices)
    
    price_every_iter_df = pd.DataFrame(price_every_iter, index=[0])
    return price_every_iter_df

def print_live_state(account, win_rate):
    """
    helper function to 'fxmanager.simulation.live.run()' function. prints the current state of the portfolio.
    """

    print('-----------------------------------------------------------------------------------------------------------')
    print(f'\n>> PROCESS MESSAGE >>  Account State At {asctime(localtime(time()))}:')
    print(f'>> PROCESS MESSAGE >> Balance          : {round(account._balance,2)}$')
    print(f'>> PROCESS MESSAGE >> Equity           : {round(account._live_equity,2)}$')
    print(f'>> PROCESS MESSAGE >> Margin           : {round(account._margin,2)}$')
    print(f'>> PROCESS MESSAGE >> Free Margin      : {round(account._live_free_margin,2)}$')
    print(f'>> PROCESS MESSAGE >> Margin Level     : {round(account._live_margin_level*100,2)}%')
    print(f'>> PROCESS MESSAGE >> Win Rate         : {round(win_rate*100,2)}%')
    print(f'>> PROCESS MESSAGE >> Open Positions   : {len(account._positions)}')
    for ticket in account._positions:
        order_type = account._positions[ticket]['order_type']
        open_price = account._positions[ticket]['open_price']
        cp = account._positions[ticket]['base_currency'] + account._positions[ticket]['quote_currency']
        print(f'                                       : [{order_type} {cp}] At Open Price: {round(open_price,5)}')
    print(f'>> PROCESS MESSAGE >> Live Profit      : {round(account._live_profit,2)}$\n')
    print(f'>> PROCESS MESSAGE >> Total Profit     : {round(account._profit,2)}$\n')

def print_final_state(account, win_rate):
    """
    helper function to 'fxmanager.simulation.live.run()' function. prints the final state of the portfolio after the simulation is finished.
    """

    print('>> PROCESS MESSAGE >> Printing Final Portfolio State ..\n')
    print(f'>> PROCESS MESSAGE >> Balance          : {round(account._balance,2)}$')
    print(f'>> PROCESS MESSAGE >> Equity           : {round(account._equity,2)}$')
    print(f'>> PROCESS MESSAGE >> Margin           : {round(account._margin,2)}$')
    print(f'>> PROCESS MESSAGE >> Free Margin      : {round(account._free_margin,2)}$')
    print(f'>> PROCESS MESSAGE >> Margin Level     : {round(account._margin_level*100,2)}%')
    print(f'>> PROCESS MESSAGE >> Open Positions   : {len(account._positions)}')
    print(f'>> PROCESS MESSAGE >> Win Rate         : {round(win_rate*100,2)}%')
    print(f'>> PROCESS MESSAGE >> Total Profit     : {round(account._profit,2)}$\n')

def close_position(account, ticket, portfolio_prices, portfolio_orders, wins, losses):
    """
    helper function to 'fxmanager.simulation.live.run()' function. closes an opened position by ticket.

    Returns:
        - portfolio_orders: pandas dataframe with history of closed positions. Each row represents a closed position.
        - wins            : integer indicating number of closed positions with positive profit.
        - losses          : integer indicating number of closed positions with nigative profit.
        - win_rate        : float indicating percentage of wins to (wins+losses).
    """

    cp = account._positions[ticket]['base_currency'] + account._positions[ticket]['quote_currency']
    open_price = account._positions[ticket]['open_price']
    volume = account._positions[ticket]['volume']
    tf = account._positions[ticket]['time_frame']
    order_type = account._positions[ticket]['order_type']
    SL = account._positions[ticket]['SL']
    TP = account._positions[ticket]['TP']
    w = account._positions[ticket]['weight']

    close_price = portfolio_prices.iloc[-1][[cp+'_ask_close', cp+'_bid_close']]
    close_price.index = ['ask', 'bid']
    position_porfit, margin_req, close_price = account.close_position(ticket=ticket, prices=close_price)
    
    order = pd.DataFrame({'Ticket': ticket,
                        'Order Type':order_type,
                        'Currency Pair':cp,
                        'Time Frame': tf,
                        'Weight': w,
                        'Volume': volume,
                        'SL':SL,
                        'TP':TP,
                        'Open Price': open_price,
                        'Close Price': close_price,
                        'Margin requirment': margin_req,
                        'Porfit': position_porfit}, index=[0])
    
    portfolio_orders = pd.concat([portfolio_orders, order], ignore_index=True)
    
    if position_porfit >= 0:
        wins += 1
    else:
        losses +=1
    
    win_rate = wins / (wins+losses)

    return portfolio_orders, wins, losses, win_rate

##########################################################################################################################
##                                                 Main Function
##########################################################################################################################

def run(account, strategy, data_dir=None, construct_portfolio=False, portfolio={}, weight_optimization=False, is_preprocessed=True,raw_data_format='',
        optimization_method='', optimization_objective='', sleep_time=1, risk_factor=1, sync_zero=False, save_logs=False, **kwargs):
    """
    starts trading simulation with live prices from MT4 EA.

    Args: 
        - account               : account object with all account information.
        - strategy              : strategy object with the trading strategy information.
        - data_dir              : string with the directory or full path to the directory in which application data is kept. If the setup() function is used to create the recommended project structure, the default None value should be used.
        - construct_portfolio   : boolean indicating whether portfolio optimization is used or not.
        - portfolio             : dictionary with the portfolio to be used for trading, keys are: (currency_pairs, time_frames, weights). This argument is only used if 'construct_portfolio' is set to False.
        - weight_optimization   : boolean indicating whether weight optimization is used in portfolio optimization. This argument is only used when 'construct_portfolio' is set to True.
        - is_preprocessed       : boolean indicating if the data of used for portfolio optimization is preprocessed or not. This argument is only used when 'construct_portfolio' is set to True.
        - raw_data_format       : dictionary with information about raw data used for portfolio optimization. This argument is only used when 'construct_portfolio' is set to True.
        - optimization_method   : string with optimization method to be used. This argument is only used when 'construct_portfolio' is set to True.
        - optimization_objective: string with optimization objective to be used. This argument is only used when 'construct_portfolio' is set to True.
        - sleep_time            : integer indicating the time every which the portfolio is updated (in seconds).
        - risk_factor           : a float with range from 0 to 1 indicating the percentage of reinvested balance.
        - sync_zero             : boolean flag, if True, the simulation starts when the seconds in current time = 0.
        - save_logs             : boolean flag, if the program logs are saved to 'data_dir\\logs\\live_simulation_logs.txt' file.
        - kwargs                : dictionary to hold any number of arguments required for the strategy object.
    Returns:
        - None
    """

    if data_dir is None:
        data_dir = join(getcwd(), 'data')
    if save_logs:
        sys.stdout = open(join(data_dir,'logs','back_test_logs.txt'), 'w')

    print('-----------------------------------------------------------------------------------------------------------')
    print('-----------------------------------------------------------------------------------------------------------')
    print(f'                                   >> {asctime(localtime(time()))} <<')
    print('-----------------------------------------------------------------------------------------------------------')
    print('-----------------------------------------------------------------------------------------------------------')

    if construct_portfolio:
        portfolio, currency_pairs, time_frames, weights = optimize_portfolio(data_dir=data_dir,
                                                                              raw_data_format=raw_data_format,
                                                                              optimization_method=optimization_method,
                                                                              optimization_objective=optimization_objective,
                                                                              weight_optimization=weight_optimization,
                                                                              is_preprocessed = is_preprocessed)
    else:
        print('\n>> SYSTEM MESSAGE >> Portfolio Construction Is Not Needed! Skipping Stages 1 & 2 ..\n')
        currency_pairs = portfolio['currency_pairs']
        time_frames = portfolio['time_frames']
        weights = portfolio['weights']


    # STAGE 3: Subscribe to The Price Feed of Currency Pairs in The Portfolio
    print('>> SYSTEM MESSAGE >> STAGE 3: Subscribing to The Price Feed of Currency Pairs in The Portfolio ..\n')
    price_feed = ps(_symbols=currency_pairs)
    price_feed.run()
    print('\n>> SYSTEM MESSAGE >> Successfully Connected To Live Price Feed!\n')

    ## STAGE 4: The Main Loop
    print('>> SYSTEM MESSAGE >> STAGE 4: Starting The Main Loop ..\n')
    
    # initialize variables
    portfolio_prices = pd.DataFrame()
    portfolio_orders = pd.DataFrame()
    wins = 0
    losses = 0
    win_rate = 0
    try:
        # wait until initial prices are available
        for cp in currency_pairs:
            while price_feed._recent_prices[cp] == 0:
                pass
        
        # wait until seconds == 0 befor starting the main loop (to sync with local time)
        if sync_zero:
            while localtime(time()).tm_sec != 0:
                pass
        
        ## Main Loop
        while not price_feed.isFinished():
            try:
                price_every_iter_df = get_price(currency_pairs=currency_pairs, price_feed=price_feed, sleep_time=sleep_time)
                portfolio_prices = pd.concat([portfolio_prices, price_every_iter_df], ignore_index=True)

                # Loop Through the opened positions and close the ones with period = 0
                tickets = list(account._positions.keys())
                for ticket in tickets:
                    period = account._positions[ticket]['period']
                    if period == 0:
                        portfolio_orders, wins, losses, win_rate = close_position(account=account,
                                                                                ticket=ticket,
                                                                                portfolio_prices=portfolio_prices,
                                                                                portfolio_orders=portfolio_orders,
                                                                                wins=wins,
                                                                                losses=losses)
                
                # Loop Through portfolio assets and add positions
                for cp, tf, w in zip(currency_pairs, time_frames, weights):
                    if tf[1].isalpha():
                        period = int(int(tf[0]) / sleep_time)
                    else:
                        period = int(int(tf[:2]) / sleep_time)
                    
                    if (portfolio_prices.index[-1] % period) == 0:
                        strategy._currency_pair = cp
                        strategy._time_frame = tf
                        orders = strategy.get_orders(prices = portfolio_prices, **kwargs)
                        order = orders.iloc[-1]
                        order_idx = orders.index[-1]
                        order_ticket = cp + '_' + tf + str(order_idx)
                        if order['order_type'] == 'hold':
                            continue
                            
                        # if the position is already opened, don't open it again
                        if order_ticket not in account._positions:
                            open_price = portfolio_prices.iloc[order_idx][[cp+'_ask_open', cp+'_bid_open']]
                            open_price.index = ['ask', 'bid']
                            is_opened = account.open_pisition(ticket = order_ticket,
                                                                base_currency = cp[:3],
                                                                quote_currency = cp[3:],
                                                                time_frame=tf,
                                                                weight = w,
                                                                SL = order['SL'],
                                                                TP = order['TP'],
                                                                order_type = order['order_type'],
                                                                prices = open_price,
                                                                period = period,
                                                                order_idx = order_idx,
                                                                risk_factor = risk_factor)
                            # if the position couldn't be opened, break out of the main loop and print account state
                            if not is_opened:
                                print('\n>> PROCESS MESSAGE >> Balance is not enough to open a new position!\n')
                                price_feed.stop()
                                print('\n>> PROCESS MESSAGE >> Closing any open positions ..\n')
                                tickets = list(account._positions.keys())
                                for ticket in tickets:
                                    portfolio_orders, wins, losses, win_rate = close_position(account=account,
                                                                                            ticket=ticket,
                                                                                            portfolio_prices=portfolio_prices,
                                                                                            portfolio_orders=portfolio_orders,
                                                                                            wins=wins,
                                                                                            losses=losses)
                                break
                if not is_opened:
                    break

                # Update account state with current prices
                account.update(prices = portfolio_prices)

                # print account state every minute
                print_live_state(account=account, win_rate=win_rate)
                
            except UnboundLocalError:
                pass

            # if 24 hours (1440 minutes) have passed, finish the program
            if len(portfolio_prices) >= 1440:
                print('\n-----------------------------------------------------------------------------------------------------------')
                print('>> PROCESS MESSAGE >> Congratulations! you have made it through the day. Closing any remaining positions ..\n')
                price_feed.stop()
                tickets = list(account._positions.keys())
                for ticket in tickets:
                    portfolio_orders, wins, losses, win_rate = close_position(account=account,
                                                                            ticket=ticket,
                                                                            portfolio_prices=portfolio_prices,
                                                                            portfolio_orders=portfolio_orders,
                                                                            wins=wins,
                                                                            losses=losses)
                break
            else:
                print('>> PROCESS MESSAGE >> Waiting for next update! to stop and save the results press CTRL+C\n')

    except KeyboardInterrupt:
        price_feed.stop()
        print('\n>> PROCESS MESSAGE >> Process is terminated by user. Closing any remaining positions ..\n')
        tickets = list(account._positions.keys())
        for ticket in tickets:
            portfolio_orders, wins, losses, win_rate = close_position(account=account,
                                                                    ticket=ticket,
                                                                    portfolio_prices=portfolio_prices,
                                                                    portfolio_orders=portfolio_orders,
                                                                    wins=wins,
                                                                    losses=losses)
    
    print('>> SYSTEM MESSAGE >> All Positions Are Closed Successfully!\n')
    print('>> SYSTEM MESSAGE >> STAGE 5: Saving Stats & Visualizations ..\n')

    # Print final state of the account
    print_final_state(account=account, win_rate=win_rate)

    # Save the optimized portfolio
    portfolio_df = pd.DataFrame(portfolio)
    portfolio_df.to_csv(join(data_dir,'stats', 'live_porfolio.csv'))

    # Save the orders
    portfolio_orders.to_csv(join(data_dir,'stats', 'live_orders.csv'))

    print('\n>> SYSTEM MESSAGE >> Execution Finished')

    if save_logs:
        sys.stdout.close()
    return

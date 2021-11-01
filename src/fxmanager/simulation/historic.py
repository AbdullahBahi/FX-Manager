#!/usr/bin/env python

"""
This module contains helper functions used internally in this module and a public function to run historical simulation.

Public Functions:
    - run(): starts trading simulation with historic prices.
"""

import sys
from os import getcwd
from os.path import join
import pandas as pd 
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

##########################################################################################################################
##                                                 Helper Functions
##########################################################################################################################

def get_prices(day, data_dir=None, time_frame='', currency_pair=''):
    """
    helper function to 'fxmanager.simulation.historic.run()' function. gets the bid/ask prices of the given currency_pair & time_frame in the selected day from the 'data_dir\\time_frames' directory.

    Args:
        - day           : integer indicating day number - starts from 0 and ends with the total number of work days in the dataset (num_days-1).
        - data_dir      : string with the directory or full path to the directory in which application data is kept. If the setup() function is used to create the recommended project structure, the default None value should be used.
        - time_frame    : a string of the timeframe from wich the prices is read.
        - currency_pair : a string of the currency pair from wich the prices is read. 
    Returns:
        - df: pandas dataframe of the bid & ask prices with columns (ask_open, bid_open, ask_close, bid_close, tick_volume) and a datetime index from the begining to the end off the day with frequency equal to time_frame.
    """

    if data_dir is None:
        data_dir = join(getcwd(), 'data')
    df = pd.read_csv(join(data_dir, 'time_frames', str(day), time_frame , currency_pair+'_'+time_frame+'.csv'), parse_dates=True)
    df.index = pd.to_datetime(df['time'])
    df.drop(['time', 'best_rets', 'wrst_rets', 'ask_sample1', 'bid_sample1', 'ask_sample2', 'bid_sample2'], axis = 1, inplace = True)
    return df

def print_final_state(account, win_rate):
    """
    helper function to 'fxmanager.simulation.historic.run()' function. prints the final state of the portfolio after the simulation is finished.
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
    helper function to 'fxmanager.simulation.historic.run()' function. closes an opened position by ticket.

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

def run(account, strategy, data_dir=None, portfolios={}, risk_factor=0.95, save_logs=False, **kwargs):
    """
    starts trading simulation with historic prices.

    Args: 
        - account               : account object with all account information.
        - strategy              : strategy object with the trading strategy information.
        - data_dir              : string with the directory or full path to the directory in which application data is kept. If the setup() function is used to create the recommended project structure, the default None value should be used.
        - portfolios            : pandas dataframe with columns (currency_pairs, time_frames, weights) and range index of length = num_days
        - risk_factor           : a float with range from 0 to 1 indicating the percentage of reinvested balance.
        - save_logs             : boolean flag, if the program logs are saved to 'data_dir\\logs\\live_simulation_logs.txt' file.
        - kwargs                : dictionary to hold any number of arguments required for the strategy object.
    Returns:
        - None
    """

    if data_dir is None:
        data_dir = join(getcwd(), 'data')
    if save_logs:
        sys.stdout = open(join(data_dir,'logs','historic_simulation_logs.txt'), 'w')

    win_rate = 0
    wins = 0
    losses = 0
    
    for day in portfolios.index:
        print('-----------------------------------------------------------------------------------------------------------')
        print('-----------------------------------------------------------------------------------------------------------')
        print('                                             >> Processing Day {} <<'.format(day))
        print('-----------------------------------------------------------------------------------------------------------')
        print('-----------------------------------------------------------------------------------------------------------')

        ## STAGE 1: Extracting Portfolio Parameters
        print('\n>> SYSTEM MESSAGE >> STAGE 1: Extracting Portfolio Parameters ..\n')
        currency_pairs = portfolios.loc[day, 'currency_pairs']
        time_frames = portfolios.loc[day, 'time_frames']
        weights = portfolios.loc[day, 'weights']
        
        ## STAGE 2 : Get The Prices And Orders Of Each Asset in The Portfolio
        print('>> SYSTEM MESSAGE >> Portfolio Parameters Are Loaded & Extracted Successfully!\n')
        print('>> SYSTEM MESSAGE >> STAGE 2: Getting Prices Of Selected Assets In The Portfolio ..\n')
        
        # Initialize empty dataframes used as placeholders for orders data over the day
        portfolio_orders = pd.DataFrame()
        
        # Initialize a dataframe to hold price updates every minute
        _ = get_prices(day=day, data_dir=data_dir, time_frame=time_frames[0], currency_pair=currency_pairs[0])
        idx = pd.date_range(_.index[0], freq='min', periods=1440)
        cols = []
        for cp in currency_pairs:
            cols.append(cp+'_bid_open')
            cols.append(cp+'_ask_open')
            cols.append(cp+'_bid_close')
            cols.append(cp+'_ask_close')
        portfolio_prices = pd.DataFrame([[0]*len(currency_pairs)*4]*1440, index=idx, columns=cols)
        for cp, tf, w in zip(currency_pairs, time_frames, weights):
            prices = get_prices(day=day, data_dir=data_dir, time_frame=tf, currency_pair=cp)
            for idx in prices.index:
                portfolio_prices.loc[[idx], [cp+'_bid_open', cp+'_ask_open', cp+'_bid_close', cp+'_ask_close']] = \
                prices.loc[[idx], ['bid_open', 'ask_open', 'bid_close', 'ask_close']].values
            
        portfolio_prices = portfolio_prices.replace(to_replace=0, method='ffill')
        portfolio_prices.index = range(len(portfolio_prices))
        portfolio_prices.index.name = 'Minutes'
        ## STAGE3: Start Placing Orders
        print('>> SYSTEM MESSAGE >> Prices Over The Day Are Extracted Successfully! ..\n')
        print('>> SYSTEM MESSAGE >> STAGE 3: Starting To Open Positions ..\n')

        # Main Loop
        for idx in portfolio_prices.index:
            try:
                # Loop Through the opened positions and close the ones with period = 0
                tickets = list(account._positions.keys())
                for ticket in tickets:
                    period = account._positions[ticket]['period']
                    if period == 0:
                        portfolio_orders, wins, losses, win_rate = close_position(account=account,
                                                                                ticket=ticket,
                                                                                portfolio_prices=portfolio_prices.loc[:idx],
                                                                                portfolio_orders=portfolio_orders,
                                                                                wins=wins,
                                                                                losses=losses)
                # Loop Through portfolio assets and add positions
                for cp, tf, w in zip(currency_pairs, time_frames, weights):
                    if tf[1].isalpha():
                        period = int(int(tf[0]))
                    else:
                        period = int(int(tf[:2]))

                    if (idx % period) == 0:
                        strategy._currency_pair = cp
                        strategy._time_frame = tf
                        orders = strategy.get_orders(prices= portfolio_prices.loc[:idx], **kwargs)
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
                                print('\n>> PROCESS MESSAGE >> Closing any open positions ..\n')
                                tickets = list(account._positions.keys())
                                for ticket in tickets:
                                    portfolio_orders, wins, losses, win_rate = close_position(account=account,
                                                                                            ticket=ticket,
                                                                                            portfolio_prices=portfolio_prices.loc[:idx],
                                                                                            portfolio_orders=portfolio_orders,
                                                                                            wins=wins,
                                                                                            losses=losses)
                                print('>> SYSTEM MESSAGE >> All Positions Are Closed Successfully!\n')

                                # Print final state of the account
                                print_final_state(account=account, win_rate=win_rate)
                                break
                if not is_opened:
                    break
                # Update account state with current prices
                account.update(prices = portfolio_prices.loc[:idx])
            except UnboundLocalError:
                pass
        if not is_opened:
            break

        print('>> PROCESS MESSAGE >> Congratulations! you have made it through the day! Closing any open positions ..\n')
        tickets = list(account._positions.keys())
        for ticket in tickets:
            portfolio_orders, wins, losses, win_rate = close_position(account=account,
                                                                        ticket=ticket,
                                                                        portfolio_prices=portfolio_prices,
                                                                        portfolio_orders=portfolio_orders,
                                                                        wins=wins,
                                                                        losses=losses)
        # Print final state of the account
        print_final_state(account=account, win_rate=win_rate)

    # Save the orders
    print('>> SYSTEM MESSAGE >> STAGE 4: Saving Stats & Visualizations ..\n')
    portfolio_orders.to_csv(join(data_dir,'stats', 'historical_simulation_orders', 'Day_'+str(day)+'_orders.csv'))
        
    print('>> SYSTEM MESSAGE >> No More Days are Left! Go get More Data!\n')
    print('>> SYSTEM MESSAGE >> Execution Finished')

    if save_logs:
        sys.stdout.close()
    return 
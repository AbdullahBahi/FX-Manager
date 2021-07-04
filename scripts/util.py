import pandas as pd
from os import getcwd
from os.path import join
import edhec_risk_kit as erk
import matplotlib.pyplot as plt
import numpy as np

CWD = join(getcwd(), '..','datasets')

time_frames = ['1min', '2min', '3min', '4min', '5min', '6min', '7min', '8min', '9min', '10min']
currency_pairs = ['AUDUSD', 'EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDCNH', 'USDDKK',
                  'USDHKD', 'USDHUF', 'USDJPY', 'USDMXN', 'USDNOK', 'USDPLN', 'USDSEK', 'USDSGD',
                  'USDZAR']

def get_rets(time_frame = '1min', ret_type='border_max'):
    """
    Description:
        - gets the specified type of returns of all currency pairs in the specified time frame
        
        - the function reads data from '/time_frames/' directory which contains preprocessed data
          for each time frame

    Parameters:
        - time_frame: a string specifying the time frame to get the data from

        - ret_type: a string specifying the type of returns to get, the available returns are: 
            - border_max, border_min: calculated given the assumption that the open and close prices 
              of a timeframe unit = the prices of the ticks at borders of the timeframe unit, the 'max'
              and 'min' refer to the best and worst performance that could be made

            - max, min:calculated given the assumption that the open and close prices 
              of a timeframe unit = the highest prices of all the ticks in the timeframe unit, the 'max'
              and 'min' refer to the best and worst performance that could be made

            - naieve_buy, naieve_sell: calculated given the assumption that we buy only or sell only using 
              the border prices. No checking for the right trade is made to calculate this one
    Returns:
        - rets: pandas DataFrame containing the required returns for each curruncy pair in a column
    """
    rets = pd.DataFrame()
    for cp in currency_pairs:
        file_name = cp + '_' + time_frame + '.csv'
        df = pd.read_csv(join(CWD, 'time_frames', time_frame, file_name))
        df.index = pd.to_datetime(df['time'])
        rets = pd.concat([rets, df[ret_type+'_rets']], ignore_index=True, axis=1)
    rets.columns = currency_pairs
    rets.index = pd.to_datetime(df['time'])
    return rets.dropna()

def get_correct_trades(time_frame = '1min', is_border=True):
    """
    Description:
        - gets the correct trades that should be made using border or high/low prices for each timeframe unit

    Parameters:
        - time_frame: see 'get_rets' description
        - is_border: boolian that is used to decide what prices to be used. if True, the border prices are used,
          if False, the high/low prices are used
    
    Returns:
        - ct: pandas DataFrame containing the correct trades for each currency pair in the specified timeframe
        - counts: pandas DataFrame containing the counts of unique values for each currency pair in 'ct' DataFrame
            - the available unique values:
                - hold: when buying or selling yield negative return
                - buy: when the prices are rising
                - sell: when the prices are falling
           
    """
    ct = pd.DataFrame()
    for cp in currency_pairs:
        file_name = cp + '_' + time_frame + '.csv'
        df = pd.read_csv(join(CWD, 'time_frames', time_frame, file_name))
        df.index = pd.to_datetime(df['time'])
        if is_border:
            col = 'border_correct_trades'
        else:
            col = 'correct_trades'
        ct = pd.concat([ct, df[col]], ignore_index=True, axis=1)
    ct.columns = currency_pairs
    ct.index = pd.to_datetime(df['time'])
    ct = ct.dropna()

    # calculate counts
    counts = pd.DataFrame()
    for j in ct.columns:
        counts[j] = ct[j].value_counts()

    return ct, counts

def get_expected_rets(time_frame='1min', win_rate=0.5, is_border=True):
    """
    Description:
        - calculates the expected returns for a given win rate using the following steps:
            1 - get the best and worst returns of the specified type (borders or high/low)
            2 - find the average returns for both beast and worst returns and use the averages 
                as fixed returns for wining or losing (i.e. average of best returns for winning
                and average of worst returns for losing)
            3 - construct a new dataframe with the same shape as best and worst returns but the
                values replaced with averages split according to 'win_ate' (i.e. if win_rate=0.5
                then half the values would be the average of best returns and the other half is 
                the average of worst returns)
            4 - calculate the compunded return of the newly constructed data frame.

    Parameters:
        - time_frame: see 'get_rets' description
        - win_rate: a float specifying the rate of winning trades made by an algorithm
        - is_border: see 'get_correct_trades' description
    
    Returns:
        - expected_compounded_rets: pandas DataFrame containing the compunded returns of each currency
          pair in the specified timeframe, calculated using the averages of best and worst returns.

        - real_compounded_rets: pandas DataFrame containing the compunded returns of each currency
          pair in the specified timeframe, calculated using REAL samples of the best and worst returns
    """
    loss_rate = 1 - win_rate

    if is_border:
        max_ret_type = 'border_max'
        min_ret_type = 'border_min'
    else:
        max_ret_type = 'max'
        min_ret_type = 'min'

    max_rets = get_rets(time_frame = time_frame, ret_type=max_ret_type)
    num_wins = int(win_rate * max_rets.shape[0])
    win_rets = max_rets.mean()
    win_rets = pd.DataFrame(win_rets).transpose()
    win_rets = win_rets.loc[win_rets.index.repeat(num_wins)].reset_index(drop=True)
    real_win_rets = max_rets.sample(num_wins)
    
    min_rets = get_rets(time_frame = time_frame, ret_type=min_ret_type)
    num_losses = int(loss_rate * max_rets.shape[0])
    loss_rets = min_rets.mean()
    loss_rets = pd.DataFrame(loss_rets).transpose()
    loss_rets = loss_rets.loc[loss_rets.index.repeat(num_losses)].reset_index(drop=True)
    real_loss_rets = min_rets.sample(num_losses)

    real_rets = pd.concat([real_win_rets, real_loss_rets], ignore_index=True)
    real_compounded_rets = (1+real_rets).prod()-1
    
    rets = pd.concat([win_rets, loss_rets])
    expected_compounded_rets = (1+rets).prod()-1
    
    # print(f'max expected compounded return in {tf} timeframe at {win_rate}% win rate: {round(expected_compounded_rets.max()*100,2)}%')
    # print(f'max real compounded return in {tf} timeframe at {win_rate}% win rate: {round(real_compounded_rets.max()*100,2)}%')

    return real_compounded_rets, expected_compounded_rets

def get_overall_rets(win_rate = 0.5, method='max', top_n=3, is_border=True):
    """
    Description:
        - iterates over all the time frames, finds the expected returns for each one at
          a given win rate, choses the best curruncy pairs from each according to the 
          specified 'method' and finally constructs a portfolio using the selected 
          currency pairs.

    Parameters:
        - win_rate: see 'get_expected_rets' description
        - method: a string specifying the criteria to be used to select currency pairs from each timeframe.
          The available methods are:
            - max: choses the highest return in each timeframe
            - positive: selects all the positive returns in each timeframe
            - top_n: selects the highest (n) returns from each timeframe
        - top_n: an integer indicating the number of top currency pairs to select from each timeframe. 
          This option is only used if the selected method is 'top_n'
        - is_border: see 'get_correct_trades' description
    
    Returns:
        - overall_expected_return: a float indicating the over all return from the constructed portfolio using
          the expected returns
        - overall_real_return: a float indicating the over all return from the constructed portfolio using
          the REAL (sampled) returns
        - portfolio: pandas dataframe containing the constructed portfolio of both expected and real returns
          and the weights that were used to calculate the overall returns
    """
    lr = 1 - win_rate
    best_expected_rets = pd.Series()
    best_real_rets = pd.Series()

    for tf in time_frames:
        real, expected = get_expected_rets(time_frame = tf, win_rate = win_rate, is_border=is_border)
        if method == 'max':
            best_expected_rets[expected.idxmax()+'_'+tf] = expected.max()
            best_real_rets[real.idxmax()+'_'+tf] = real.max()
        elif method == 'positive':
            expected_pos_idxs = expected.index[expected>0]
            real_pos_idxs = expected.index[real>0]
            for i in expected_pos_idxs:
                best_expected_rets[i+'_'+tf] = expected[i]
            for i in real_pos_idxs:
                best_real_rets[i+'_'+tf] = real[i]
        elif method == 'top_n':
            for i in expected.nlargest(top_n).index:
                best_expected_rets[i+'_'+tf] = expected[i]
            for i in real.nlargest(top_n).index:
                best_real_rets[i+'_'+tf] = real[i]
    
    weights = best_expected_rets / best_expected_rets.sum()
    
    overall_expected_return = (weights * best_expected_rets).sum()
    overall_real_return = (weights * best_real_rets).sum()

    ## Save results
    portfolio = pd.DataFrame()
    portfolio = pd.concat([portfolio, best_expected_rets], ignore_index=True, axis=1, sort=False)
    portfolio = pd.concat([portfolio, best_real_rets], ignore_index=True, axis=1, sort=False)
    portfolio = pd.concat([portfolio, weights], ignore_index=True, axis=1, sort=False)
    portfolio.columns = ['Expexted Returns', 'Real Returns', 'Weights']

    return overall_real_return, overall_expected_return, portfolio

def plot_expected_rets(num_win_rates = 11, method = 'max', top_n = 3, is_border=True):
    """
    Description:
        - iterates over a set of linearly spaced win rates, constructs a portfolio for each
          one, calculates the overall returns and plots the values for each win rate

    Parameters:
        - num_win_rates: an interger indicating the number of win rates to iterate over 
        - method: see 'get_overall_rets' description
        - top_n: see 'get_overall_rets' description
        - is_border: see 'get_correct_trades' description
    
    Returns:
        - ax: matplotlib axis object containg the plot
    """
    expected_returns = []
    real_returns = []
    portfolios = []
    win_rates = list(np.linspace(0,1,num_win_rates))
    for i in win_rates:
        print(f'calculating expected returns for {round(i*100,2)}% win rate .. ')
        overall_real_return, overall_expected_return, portfolio = get_overall_rets(win_rate = i, method = method, top_n = top_n, is_border=is_border)
        expected_returns.append(overall_expected_return)
        real_returns.append(overall_real_return)
        portfolios.append(portfolio)
    
    returns = pd.DataFrame({'real':real_returns,
                            'expected':expected_returns}, index=win_rates)
    returns.index.name = 'Win Rates'

    portfolios_df = pd.DataFrame({'portfolios': portfolios}, index=win_rates)

    if is_border:
        returns.to_csv(join(CWD, 'stats', 'overall_returns_'+method+'Method_Border'+'.csv'))
        portfolios_df.to_csv(join(CWD, 'stats', 'border_portfolios_'+ method +'Method.csv'))
    else:
        returns.to_csv(join(CWD, 'stats', 'overall_returns_'+method+'Method_noBorder'+'.csv'))
        portfolios_df.to_csv(join(CWD, 'stats', 'noBorder_portfolios_'+ method +'Method.csv'))

    ax = returns.plot(kind='line', legend=True)
    plt.show()

    return ax

if __name__ == '__main__':
    n_wr = 11
    plot_expected_rets(num_win_rates = n_wr, method = 'max', top_n = 3, is_border = True)

    
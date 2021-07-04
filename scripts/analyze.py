import pandas as pd
from os import listdir, getcwd, mkdir
from os.path import isfile, join
import math
import edhec_risk_kit as erk

cwd = join(getcwd(), '..', 'datasets')


timeframes = ['1min', '2min', '3min', '4min', '5min', '6min', '7min', '8min', '9min', '10min']
currency_pairs = ['AUDUSD', 'EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDCNH', 'USDDKK',
                  'USDHKD', 'USDHUF', 'USDJPY', 'USDMXN', 'USDNOK', 'USDPLN', 'USDSEK', 'USDSGD',
                  'USDZAR']

for i in timeframes:
    # print(f'analyzing data from {i} timeframe ..')
    tf_stats = pd.DataFrame()
    for cp in currency_pairs:
        df = pd.read_csv(join(cwd, 'time_frames', i , cp+'_'+i+'.csv'), parse_dates=True) 
        df.index = pd.to_datetime(df['time'])
        # Calculate compounded returns
        comp_max_rets = (1+df['max_rets']).prod()-1
        comp_min_rets = (1+df['min_rets']).prod()-1
        comp_naieve_buy_rets = (1+df['naieve_buy_rets']).prod()-1
        comp_naieve_sell_rets = (1+df['naieve_sell_rets']).prod()-1

        # Calculate Average rets
        avg_max_rets = df['max_rets'].mean()
        avg_min_rets = df['min_rets'].mean()
        avg_naieve_buy_rets = df['naieve_buy_rets'].mean()
        avg_naieve_sell_rets = df['naieve_sell_rets'].mean()

        # Calculate returns volatility
        max_vol = df['max_rets'].std()
        min_vol = df['min_rets'].std()
        naieve_buy_vol = df['naieve_buy_rets'].std()
        naieve_sell_vol = df['naieve_sell_rets'].std()

        # Calculate compounded volatility
        num_records = df.shape[0]
        comp_max_vol = max_vol * (num_records**0.5)
        comp_min_vol = min_vol * (num_records**0.5)
        comp_naieve_buy_vol = naieve_buy_vol * (num_records**0.5)
        comp_naieve_sell_vol = naieve_sell_vol * (num_records**0.5)

        # Calculate return on risk ratios
        max_ror = comp_max_rets / comp_max_vol
        min_ror = comp_min_rets / comp_min_vol
        naieve_buy_ror = comp_naieve_buy_rets / comp_naieve_buy_vol
        naieve_sell_ror = comp_naieve_sell_rets / comp_naieve_sell_vol

        # Calculate adjusted return on risk ratios (sharp ratios)
        rf = 0.001
        max_sharp_ror = (comp_max_rets-rf) / comp_max_vol
        min_sharp_ror = (comp_min_rets-rf) / comp_min_vol
        naieve_buy_sharp_ror = (comp_naieve_buy_rets-rf) / comp_naieve_buy_vol
        naieve_sell_sharp_ror = (comp_naieve_sell_rets-rf) / comp_naieve_sell_vol

        # # Calculate Jarque Bera scores
        max_JB = erk.is_normal(df['max_rets'])
        min_JB = erk.is_normal(df['min_rets'])
        naieve_buy_JB = erk.is_normal(df['naieve_buy_rets'])
        naieve_sell_JB = erk.is_normal(df['naieve_sell_rets'])

        # # Calculate Value at Risk VaR (Historic)
        max_var = erk.var_historic(df['max_rets'])
        min_var = erk.var_historic(df['min_rets'])
        naieve_buy_var = erk.var_historic(df['naieve_buy_rets'])
        naieve_sell_var = erk.var_historic(df['naieve_sell_rets'])

        
        tf_stats[cp] = pd.Series({'comp_max_rets':comp_max_rets,
                        'comp_min_rets':comp_min_rets,
                        'comp_naieve_buy_rets':comp_naieve_buy_rets,
                        'comp_naieve_sell_rets':comp_naieve_sell_rets,
                        'avg_max_rets':avg_max_rets,
                        'avg_min_rets':avg_min_rets,
                        'avg_naieve_buy_rets':avg_naieve_buy_rets,
                        'avg_naieve_sell_rets':avg_naieve_sell_rets,
                        'max_vol':max_vol,
                        'min_vol':min_vol,
                        'naieve_buy_vol':naieve_buy_vol,
                        'naieve_sell_vol':naieve_sell_vol,
                        'comp_max_vol':comp_max_vol,
                        'comp_min_vol':comp_min_vol,
                        'comp_naieve_buy_vol':comp_naieve_buy_vol,
                        'comp_naieve_sell_vol':comp_naieve_sell_vol,
                        'max_ror':max_ror,
                        'min_ror':min_ror,
                        'naieve_buy_ror':naieve_buy_ror,
                        'naieve_sell_ror':naieve_sell_ror,
                        'max_sharp_ror':max_sharp_ror,
                        'min_sharp_ror':min_sharp_ror,
                        'naieve_buy_sharp_ror':naieve_buy_sharp_ror,
                        'naieve_sell_sharp_ror':naieve_sell_sharp_ror,
                        'max_JB':max_JB,
                        'min_JB':min_JB,
                        'naieve_buy_JB':naieve_buy_JB,
                        'naieve_sell_JB':naieve_sell_JB,
                        'max_var':max_var,
                        'min_var':min_var,
                        'naieve_buy_var':naieve_buy_var,
                        'naieve_sell_var':naieve_sell_var
                        })
    print('average compunded returns of max_rets in {} time frame: {}%'.format(i,round(tf_stats.loc['comp_min_vol'].mean()*100,2)))
    # tf_stats.to_csv(join(cwd, 'stats', i+'_stats.csv'))
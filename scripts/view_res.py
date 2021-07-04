import pandas as pd
from os import listdir, getcwd, mkdir
from os.path import isfile, join
import math

cwd = join(getcwd(), '..', 'datasets')

timeframes = ['1min', '2min', '3min', '4min', '5min', '6min', '7min', '8min', '9min', '10min']
currency_pairs = ['AUDUSD', 'EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDCNH', 'USDDKK',
                  'USDHKD', 'USDHUF', 'USDJPY', 'USDMXN', 'USDNOK', 'USDPLN', 'USDSEK', 'USDSGD',
                  'USDZAR']

for i in timeframes:
    print(f'viewing returns from {i} timeframe >>')
    for cp in currency_pairs:
        df = pd.read_csv(join(cwd, 'time_frames', i , cp+'_'+i+'.csv'), parse_dates=True) 
        df.index = pd.to_datetime(df['time'])
        print(f"    Naieve sell compounded return for {cp} : {round(((1+df['naieve_sell_rets']).prod()-1)*100, 2)}%")
        # print(f"minimum     compounded return: {round(((1+df['min_rets']).prod()-1)*100, 2)}%")
        # print(f"Naieve buy  compounded return: {round(((1+df['naieve_buy_rets']).prod()-1)*100, 2)}%")
        # print(f"Naieve sell compounded return: {round(((1+df['naieve_sell_rets']).prod()-1)*100, 2)}%")
    
    

# for i in timeframes:
#     print(f'\nMaximum wealth in {i} = {math.floor(wealth_df[i].max()* 100)/100}   in   {wealth_df[i].idxmax()}   with a rate of   {math.floor((wealth_df[i].max()-1000)/1000 * 100)}%   FROM   {time_df[i][wealth_df[i].idxmax()]}   to   2021-06-18')

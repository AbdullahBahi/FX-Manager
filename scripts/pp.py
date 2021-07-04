import pandas as pd
from os import listdir, getcwd, mkdir
from os.path import isfile, join

cwd = join(getcwd(), '..', 'datasets')

timeframes = ['1min', '2min', '3min', '4min', '5min', '6min', '7min', '8min', '9min', '10min']
file_names = [f for f in listdir(join(cwd, 'raw_data')) if isfile(join(cwd, 'raw_data', f))]

def process(df, tf):
    # initialize placeholders for final data
    ask_open = []
    bid_open = []
    ask_close = []
    bid_close = []
    ask_high = []
    bid_high = []
    ask_low	= []
    bid_low	= []
    spread_open = []
    spread_close = []
    ask_volume = []
    bid_volume = []
    tick_volume = []
    correct_trades = []
    max_rets = []
    min_rets= []
    naieve_buy_rets = []
    naieve_sell_rets = []
    border_correct_trades = []
    border_max_rets = []
    border_min_rets = []

    # get a DataFrame that is grouped by the specified timeframe
    grouped = pd.DataFrame(df.groupby(pd.Grouper(freq=tf)), columns=['time', 'sub_dataframes'])

    for dataframe in grouped['sub_dataframes']:
        if dataframe.shape[0] != 0:
            ask_open.append(dataframe['ask'][0])
            bid_open.append(dataframe['bid'][0])
            ask_close.append(dataframe['ask'][-1])
            bid_close.append(dataframe['bid'][-1])
            ask_high.append(dataframe['ask'].max())
            bid_high.append(dataframe['bid'].max())
            ask_low.append(dataframe['ask'].min())
            bid_low.append(dataframe['bid'].min())
            spread_open.append(dataframe['ask'][0] - dataframe['bid'][0])
            spread_close.append(dataframe['ask'][-1] - dataframe['bid'][-1])
            
            ask_volume.append(dataframe['askvolume'].sum())
            bid_volume.append(dataframe['bidvolume'].sum())
            tick_volume.append(dataframe.shape[0])

            buy_trade_condition  = (dataframe['bid'].idxmax()-dataframe['ask'].idxmin()).days >= 0 and (bid_high[-1]-ask_low[-1]) > 0
            sell_trade_condition = (dataframe['ask'].idxmin()-dataframe['bid'].idxmax()).days >= 0 and (bid_high[-1]-ask_low[-1]) > 0
            if buy_trade_condition:
                correct_trades.append('buy')
                max_rets.append((bid_high[-1]-ask_low[-1]) / ask_low[-1])
                min_rets.append((bid_low[-1]-ask_high[-1]) / bid_low[-1])
            elif sell_trade_condition:
                correct_trades.append('sell')
                max_rets.append((bid_high[-1]-ask_low[-1]) / bid_high[-1])
                min_rets.append((bid_low[-1]-ask_high[-1]) / ask_high[-1])
            else:
                correct_trades.append('hold')
                max_rets.append(0)
                if (dataframe['bid'].idxmax()-dataframe['ask'].idxmin()).days >= 0:
                    min_rets.append((bid_low[-1]-ask_high[-1]) / bid_low[-1])
                else:
                    min_rets.append((bid_low[-1]-ask_high[-1]) / ask_high[-1])

            naieve_buy_rets.append((dataframe['bid'][-1]-dataframe['ask'][0])/dataframe['ask'][0])
            naieve_sell_rets.append((dataframe['bid'][0]-dataframe['ask'][-1])/dataframe['bid'][0])

            border_buy_trade_condition  = (bid_close[-1]-ask_open[-1]) > 0
            border_sell_trade_condition = (bid_open[-1]-ask_close[-1]) > 0
            if border_buy_trade_condition:
                border_correct_trades.append('buy')
                border_max_rets.append((bid_close[-1]-ask_open[-1]) / ask_open[-1])
                border_min_rets.append((bid_open[-1]-ask_close[-1]) / bid_open[-1])
            elif border_sell_trade_condition:
                border_correct_trades.append('sell')
                border_max_rets.append((bid_open[-1]-ask_close[-1]) / bid_open[-1])
                border_min_rets.append((bid_close[-1]-ask_open[-1]) / ask_open[-1])
            else:
                border_correct_trades.append('hold')
                border_max_rets.append(0)
                if ask_open[-1] >= ask_close[-1]:
                    border_min_rets.append((bid_close[-1]-ask_open[-1]) / ask_open[-1])
                else:
                    border_min_rets.append((bid_open[-1]-ask_close[-1]) / bid_open[-1])


        else:
            ask_open.append(ask_close[-1])
            bid_open.append(bid_close[-1])
            ask_close.append(ask_close[-1])
            bid_close.append(bid_close[-1])
            ask_high.append(ask_high[-1])
            bid_high.append(bid_high[-1])
            ask_low.append(ask_low[-1])
            bid_low.append(bid_low[-1])
            spread_open.append(spread_close[-1])
            spread_close.append(spread_close[-1])
            
            ask_volume.append(0)
            bid_volume.append(0)
            tick_volume.append(0)

            correct_trades.append('hold')
            max_rets.append(0)
            min_rets.append(0)

            naieve_buy_rets.append(0)
            naieve_sell_rets.append(0)

            border_correct_trades.append('hold')
            border_max_rets.append(0)
            border_min_rets.append(0)

    final_df = pd.DataFrame({'ask_open':ask_open,
                'bid_open':bid_open,
                'ask_close':ask_close,
                'bid_close':bid_close,
                'ask_high':ask_high,
                'bid_high':bid_high,
                'ask_low':ask_low,
                'bid_low':bid_low,
                'spread_open':spread_open,
                'spread_close':spread_close,
                'ask_volume':ask_volume,
                'bid_volume':bid_volume,
                'tick_volume':tick_volume,
                'correct_trades':correct_trades,
                'max_rets':max_rets,
                'min_rets':min_rets,
                'naieve_buy_rets':naieve_buy_rets,
                'naieve_sell_rets':naieve_sell_rets,
                'border_correct_trades':border_correct_trades,
                'border_max_rets':border_max_rets,
                'border_min_rets':border_min_rets
                }, index=pd.to_datetime(grouped['time']))

    return final_df

for i in timeframes:
    print('Processing {} Timeframe ..'.format(i))
    for file_name in file_names:
        print('    Processing {} Currency pair ..'.format(file_name[:6]))
        # read basic currency pair bid/ask data
        df = pd.read_csv(join(cwd, 'raw_data', file_name))
        # unify all column strings using lower() and strip()
        df.columns = df.columns.str.lower()
        # use 'gmt time' column as an index to the data
        df.index = pd.to_datetime(df['gmt time'], format="%d.%m.%Y %H:%M:%S.%f")
        # drop the 'gmt time' column
        df.drop(['gmt time'], axis = 1, inplace = True)
        # calculate other required columns
        df = process(df=df, tf=i)
        # save results
        df.to_csv(join(cwd, 'time_frames', i , file_name[:6]+'_'+i+'.csv'))
        
from numpy import inf

class account():
    def __init__(self, balance = 100000.0, acount_type = 'standard', account_currency = 'usd', leverage = 0.01):
        ## constants
        LOT_SIZES = {"standard":100000.0, "mini":10000.0, "micro":1000.0, "nono":100.0}
        self._LOT_SIZE = LOT_SIZES[acount_type.strip().lower()]
        self._LEVERAGE = leverage
        self._ACCOUNT_CURRENCY = account_currency.strip().lower()

        self._balance = balance ## account balance (updated every time a trade is closed)
        self._equity = balance ## balance + closed_profit(updated every time a trade is closed)
        self._live_equity = balance ## balance + live_profit (updated every time unit using close price)
        self._margin = 0.0 ## required deposit to hold current trades (updated every time a trade is opened  or closed)
        self._free_margin = balance ## equity - margin (updated every time a trade is opened  or closed)
        self._live_free_margin = balance ## live equity - margin (updated every time unit using close price)
        self._margin_level = inf ## equity / margin (updated every time a trade is opened  or closed)
        self._live_margin_level = inf ## live equity / margin (updated every time unit using close price)
        self._closed_profit = 0.0 ## final profit (updated every time a trade is closed)
        self._live_profit = 0.0 ## current profit  (updated every time unit using close price)
        self._open_profit = 0.0 ## expected profit - calculated using TP for each trade (updated every time a trade is opened  or closed)
        self._open_loss = 0.0 ## expected loss - calculated using SL for each trade (updated every time a trade is opened or closed)
        self._risk_reward_ratio = 0.0 ## expected risk reward ratio: (open_loss / open_profit) (updated every time a trade is opened or closed)
        self._trades = {} ## dictionary to hold current trades {"Ticket":{..Trade properties}, ..} (updated every time a trade is opened or closed)
    
    def get_lot_value(self, price, lot_size):
        return price * lot_size
    
    def get_margin(self, lot_value, leverage, volume):
        return lot_value * leverage * volume
    
    def get_profit(self, open_lot_value, close_lot_value, volume, order_type):
        order_types = {"sell":-1.0, "buy":1.0} ## must set profit to (close - open)
        return (close_lot_value - open_lot_value) * volume * order_types[order_type.strip().lower()]
    
    def _add_trade(self, ticket, base_currency, quote_currency, volume, SL, TP, order_type, prices):
        
        if not(base_currency != self._ACCOUNT_CURRENCY and quote_currency != self._ACCOUNT_CURRENCY):
            # FIRST GET OPEN PRICE
            price_types = {"sell":"bid", "buy":"ask"}
            open_price = prices[base_currency + quote_currency][price_types[order_type]]
            if base_currency == self._ACCOUNT_CURRENCY:
                open_price = 1 / open_price

            # NOW UPDATE PORTFOLIO STATE
            ## 1 ## Margin
            open_lot_value = self.get_lot_value(open_price, self._LOT_SIZE)
            self._margin += self.get_margin(lot_value = open_lot_value, leverage = self._LEVERAGE, volume = volume)
            
            ## 2 ## Free Margin
            self._free_margin = self._equity - self._margin

            ## 3 ## Margin Level
            self._margin_level = abs((self._equity / self._margin) * 100)
            
            ## 4 ## Open Profit
            if base_currency == self._ACCOUNT_CURRENCY:
                TP = 1 / TP
            close_lot_value_TP = self.get_lot_value(TP, self._LOT_SIZE) ## base/quote lot value at TP close
            trade_profit = self.get_profit(open_lot_value, close_lot_value_TP, volume, order_type)
            self._open_profit += trade_profit

            ## 5 ## Open loss
            if base_currency == self._ACCOUNT_CURRENCY:
                SL = 1 / SL
            close_lot_value_SL = self.get_lot_value(SL, self._LOT_SIZE) ## base/quote lot value at SL close
            trade_loss = self.get_profit(open_lot_value, close_lot_value_SL, volume, order_type)
            self._open_loss += trade_loss
            
            ## 6 ## Risk/Reward Ratio
            risk_reward_ratio = abs(trade_loss / trade_profit)
            self._risk_reward_ratio = abs(self._open_loss / self._open_profit)

            ## 7 ## Trades
            self._trades[ticket] = {
                'ticket': ticket,
                'order_type': order_type,
                'volume': volume,
                'base_currency': base_currency,
                'quote_currency': quote_currency,
                'open_price': open_price,
                'SL': SL,
                'TP': TP,
                'trade_profit': trade_profit,
                'trade_loss': trade_loss,
                'live_profit': 0,
                'risk_reward_ratio': risk_reward_ratio
            }
        
            
        else:
            print("Trade expected profit cannot be calculated! Currency pair must contain account currency.")
        

    def _close_trade(self, ticket, loss = False):

        # FIRST GET TRADE PARAMETERS
        order_type = self._trades[ticket]['order_type']
        volume = self._trades[ticket]['volume']
        base_currency = self._trades[ticket]['base_currency']
        quote_currency = self._trades[ticket]['quote_currency']
        open_price = self._trades[ticket]['open_price']
        SL = self._trades[ticket]['SL']
        TP = self._trades[ticket]['TP']
        trade_profit = self._trades[ticket]['trade_profit']
        trade_loss = self._trades[ticket]['trade_loss']
        risk_reward_ratio = self._trades[ticket]['risk_reward_ratio']

        # NOW UPDATE PORTFOLIO STATE
        ## 1 ## Closed Profit
        if loss:
            self._closed_profit += trade_loss
        else:
            self._closed_profit += trade_profit

        ## 2 ## balance
        self._balance += self._closed_profit

        ## 3 ## Equity
        self._equity = self._balance

        ## 4 ## Margin
        open_lot_value = self.get_lot_value(open_price, self._LOT_SIZE)
        self._margin += self.get_margin(lot_value = open_lot_value, leverage = self._LEVERAGE, volume = volume)
        
        ## 5 ## Free Margin
        self._free_margin = self._equity - self._margin

        ## 6 ## Margin Level
        self._margin_level = abs((self._equity / self._margin) * 100)
        
        ## 7 ## Open Profit
        self._open_profit -= trade_profit

        ## 8 ## Open loss
        self._open_loss -= trade_loss
        
        ## 9 ## Risk/Reward Ratio
        if self._open_profit != 0:
            self._risk_reward_ratio = abs(self._open_loss / self._open_profit)

        ## 10 ## Trades
        self._trades.pop(ticket)

    
    def _update(self, prices):
        # UPDATE PORTFOLIO STATE
        ## 1 ## Live Profit
        self._live_profit = 0.0
        for i in self._trades:
            # Get required trade parameters
            order_type = self._trades[i]['order_type']
            volume = self._trades[i]['volume']
            base_currency = self._trades[i]['base_currency']
            quote_currency = self._trades[i]['quote_currency']
            open_price = self._trades[i]['open_price']
            
            # Get current price
            price_types = {"sell":"ask", "buy":"bid"} ## note that bid and ask are reversed because it's a CLOSE price
            current_price = prices[base_currency + quote_currency][price_types[order_type]]
            if base_currency == self._ACCOUNT_CURRENCY:
                current_price = 1 / current_price

            open_lot_value = self.get_lot_value(open_price, self._LOT_SIZE)
            close_lot_value_current = self.get_lot_value(current_price, self._LOT_SIZE) ## base/quote lot value at if trade is closed at current price
            live_profit = self.get_profit(open_lot_value, close_lot_value_current, volume, order_type)
            self._trades[i]['live_profit'] = live_profit
            self._live_profit += live_profit

        ## 2 ## Live Equity
        self._live_equity = self._balance + self._live_profit

        ## 3 ## Live Free Margin
        self._live_free_margin = self._live_equity - self._margin

        ## 4 ## Live Margin Level
        self._live_margin_level = (self._live_equity / self._margin) * 100 


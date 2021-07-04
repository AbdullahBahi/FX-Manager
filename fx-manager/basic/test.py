from docxtpl import DocxTemplate
from time import sleep
from portfolio import account

## Account information
blnc = 100000.0
acc_type = 'standard'
acc_crncy = 'usd'
lvrg = 0.01

## Trade information
ticket = 0
base_currency = 'usd'
quote_currency = 'eur'
volume = 1.0
SL = 0.82713
TP = 0.82102
order_type = 'buy'
bid = 0.82597
ask = 0.82577
symbol = base_currency+quote_currency
prices = {symbol:{'bid':bid, 'ask':ask}}

# Create a porfolio object
pf = account(balance = blnc, acount_type = acc_type, account_currency = acc_crncy, leverage = lvrg)

# Add a trade to the object
pf._add_trade(ticket, base_currency, quote_currency, volume, SL, TP, order_type, prices)

# Render automated report
template = DocxTemplate('account.docx')
template_params = pf.__dict__
template_params.update(pf.__dict__['_trades'][ticket])
template.render(template_params)
template.save('New_portfolio.docx')

# Update the object state
for i in range(10):
    prices = {symbol:{'bid':bid+(i*0.00050), 'ask':ask+(i*50)}}
    pf._update(prices)
    print(f'Equity: {pf._live_equity}             Free Margin: {pf._live_free_margin}              Margin Level: {pf._live_margin_level}             Profit: {pf._live_profit}')
    sleep(1)

# Close a trade
pf._close_trade(ticket)

print(pf.__dict__)
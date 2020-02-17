import pandas as pd
from iexfinance.stocks import get_market_gainers, get_market_losers, get_market_in_focus
import csv

# My funtions
from MYfuncs import RH_funcs as rhf
from secrets import rh_QR, rh_user, rh_password, iex_token

# This requires 2FA
from Robinhood import Robinhood
rh = Robinhood()
rh.login(username=rh_user, password=rh_password, qr_code=rh_QR)
       
        
losers = get_market_losers(token=iex_token)
losers


# Colecting information, so will be for future work
columns=['symbol','latestPrice', 'peRatio', 'iexAskPrice', 'iexBidPrice', 'iexVolume', 'avgTotalVolume']
universe = pd.DataFrame(columns=columns)

for i, loser in enumerate(losers):
    universe.loc[i] = [loser['symbol'], loser['latestPrice'], loser['peRatio'], loser['iexAskPrice'], loser['iexBidPrice'], loser['iexVolume'], loser['avgTotalVolume']]


# define allocations to be 5% of the equity availible
equity5 = rh.equity() / 20

# Filter our universe down, price has to be less than 5% of the equity value, and trading volume needs to be greater than 100k
universeList = universe[(universe['latestPrice']<equity5) & (universe['avgTotalVolume']>100000)]['symbol']
# universeList.set_index('symbol', inplace=True)
# universeList.to_csv('universList.csv', sep=",", columns=['symbol'], header=False, index=False, line_terminator='')
universeList = universeList.tolist()
universeList

# with open('universeList.csv', 'w') as f:
#     wr = csv.writer(f, quoting=csv.QUOTE_ALL)
#     wr.writerow(universeList)

# So now this is the part where we buy these stocks
outstanding_orders =[]
for tick in universeList:
    print(tick)
    price_temp = round(float(rhf.get_RH_Price(tick)), 2)
    quant = round((equity5) / price_temp, 0)
    print(quant)
    bo = rhf.buyStock_MKT(ticker=tick, quantity=quant, tif="GTC");
    try:
        outstanding_orders.append(bo.json()['id'])
    except Exception:
        outstanding_orders.append(bo[0].json()['id'])
        
outstanding_orders
# Careful, displays account info


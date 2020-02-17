
# Import libraries
import datetime as dt
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import time
import os

# Import my functions and API keys:
from MYfuncs import RH_funcs as rhf

# Determine OS and set DATA location
if os.name == 'nt':
    DATA_LOC = "DATA\\"  # Windows
else:
    DATA_LOC = "DATA/"  # Linux

# Import what we'll be trading on today [ticker: price, quantity, purchase price]
triggers = pd.read_csv(DATA_LOC + 'daily_setters.csv')
tickers = triggers.columns.tolist()
print(triggers)

now = dt.datetime.now()
data = pd.DataFrame()
# tp = pd.DataFrame()

now = dt.datetime.now()
my_dt = dt.datetime.strftime(now, "%H:%M:%S")
roll = 15
fakin_it = [triggers.iloc[0].tolist()] * roll
# print(fakin_it)
tp = pd.DataFrame(np.asarray(fakin_it).reshape(roll,len(fakin_it[0])), columns=tickers, index=pd.date_range(my_dt, periods=roll, freq='S'))
data = pd.concat([data,tp], sort=True)

delta = dt.timedelta(0,30)

while len(tickers) > 0:
    
    # Set time delay, in future may do 30 sec for first hour, then 1m after that... (future)
    if dt.datetime.now() > (now + delta):
        
        # Call the getPrices function
        prices = rhf.getPrices(tickers)
        
        # Update the timer
        now = dt.datetime.now()
        my_dt = dt.datetime.strftime(now, "%H:%M:%S")
        
        # Convert Prices to a DataFrame, then add it to data, calculate SMA
        # Note: used snipped for expanding prices with random data, need cleaner indexing option (future)
        tp = pd.DataFrame(np.asarray(prices).reshape(1,len(prices)), columns=tickers, index=pd.date_range(my_dt, periods=1, freq='S'))
        data = pd.concat([data,tp], sort=True)
        print(data.tail(3))
        sma = data.rolling(roll).mean()
        print(sma.tail(1))
        
        ### SHOULD WE TRADE? ###
        
        # Are we 3% over the trigger value?
        for tick in tickers:
            
            ##### Daily Exit Strategy #####
            # Is the current price greater than the 3% trigger price?
            if data[tick][-1] > (triggers.iloc[0][tick] * 1.03):
                
                # Things are on rise, create the 30% limit order
                print("{} is on the rise".format(tick))
                
                # This will be where we have the creep-down function (future)
                # Basically we want to allow the stock to rise as much as possible,
                # Then sell once the price is relatively stable, or fallying
                
                
                # Avoid SMA NaN errors when kicking off:
                if not sma.isnull().values.all():
                    
                    # Trigger a Positve Market Sell
                    if data[tick][-1] <= sma[tick][-1]:
                        print("Time to sell {}".format(tick))
#                         print(rh.equity())
#                         time.sleep(1) #DEBUG

                        # Sell the stock at the SMA price (should only be slightly higher... *in theory*)
                        so, resp = rhf.sellStock_MKT(
                            ticker=tick, 
                            quantity=round(float(triggers.iloc[1][tick]),4), 
                            tif='GTC'
                        )
                        print(so)
                        tickers.remove(tick)
                
            # Is the current price less than the trigger price?
            if data[tick][-1] < (triggers.iloc[0][tick] * 0.97):
                print("We've dropped 3 percent today for {}, BAIL!".format(tick))
                so, resp = rhf.sellStock_MKT(
                    ticker=tick, 
                    quantity=round(float(triggers.iloc[1][tick]),4), 
                    tif='GTC'
                )
                print(so)
                tickers.remove(tick)

            
            ##### Long Term Exit Safety #####
            # Are we 5% below the purchase price? (at any pt in time, bail)
            if data[tick][-1] < (triggers.iloc[2][tick] * 0.97):
                print("We're 5 percent below the purchase price for {}, BAIL!".format(tick))            
                so, resp = rhf.sellStock_MKT(
                    ticker=tick, 
                    quantity=round(float(triggers.iloc[1][tick]),4), 
                    tif='GTC'
                )
                print(so)
                try:
                    tickers.remove(tick)
                except Exception:
                    pass
                    
                # Initiate a Market Sell (maybe a stop-loss in the future)
                    # WANT: to send "tick" to a fuction that sells it,
                    # Need: to find a way to link ticker to any outstanding order, and cancel it
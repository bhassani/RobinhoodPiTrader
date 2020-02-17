import pandas as pd
from MYfuncs import RH_funcs as rhf
import os


if os.name == 'nt':
    DATA_LOC = "DATA\\"  # Windows
else:
    DATA_LOC = "DATA/"  # Linux
    
    
### Load current holdings, drop anything we don't want to trade today, save in the format 'exiter.py' will use ###
currents = rhf.currentHoldings()
ignore = pd.read_csv(DATA_LOC + 'ignore.csv')
ignore = ignore.columns.tolist()
for i in range(len(ignore)):
    if ignore[i] in currents:
        print("We're note looking to trade {} today".format(ignore[i]))
        currents.pop(ignore[i])

df = pd.DataFrame(currents)
print(df)
df.to_csv(DATA_LOC + 'daily_setters.csv', index=False)
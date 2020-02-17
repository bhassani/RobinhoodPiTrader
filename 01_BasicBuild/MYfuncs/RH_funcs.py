# Resources
# https://github.com/LichAmnesia/Robinhood
# https://towardsdatascience.com/step-by-step-building-an-automated-trading-system-in-robinhood-807d6d929cf3

# Point to the packages folder
# import sys
# sys.path.append('D:\\Dropbox\\CODE\\Python\\Projects\\')     # Location of my scripts/packages
# DATA_LOC = 'D:\\Dropbox\\CODE\\Python\\Projects\\DATA\\'     # Windows

# Import libraries
import requests
from bs4 import BeautifulSoup
import requests_html
import datetime as dt
import lxml.html as lh
import numpy as np
import pandas as pd
import re
from datetime import datetime
from datetime import timedelta
import time
import unidecode                    #used to convert accented words
import sys

# My Packages
from secrets import rh_QR, rh_user, rh_password, iex_token, unibit_token

# This requires setup Robinhood with 2FA
from Robinhood import Robinhood
global rh
rh = Robinhood()
global login_response 
login_response = False
login_response = rh.login(username=rh_user, password=rh_password, qr_code=rh_QR)

# Setup IEX:
from iexfinance.stocks import Stock

# Setup UniBit:
from unibit_api_v1.stockprice import StockPrice
sp = StockPrice(key=unibit_token)

###################################################################################
# My Defined Functions
###################################################################################

def buyStock_LIMIT(ticker, quantity, tif, price):
    """ Buy a Stock with limit price"""
    
    stock_url = rh.get_quote(ticker)['instrument']
#     print(stock_url)
    buy_order = rh.place_limit_buy_order(
        instrument_URL=stock_url,
        symbol=ticker,
        time_in_force=tif,
        quantity=quantity,
        price=price,
        )
     
    # sometimes the buy_order comes back as a tuple, and sometimes not... so, fix it
    try:
        buy_order = buy_order[0]
    except Exception:
        buy_order = buy_order
        
    if buy_order.status_code == 201:
        resp = "Order Placed Successfully at {}".format(buy_order.json()['price'])
    else:
        resp = "Something went wrong"
    return buy_order, resp



def sellStock_LIMIT(ticker, quantity, tif, price):
    """ Sell a Stock with limit price"""
    
    stock_url = rh.get_quote(ticker)['instrument']
#     print(stock_url)
    sell_order = rh.place_limit_sell_order(
        instrument_URL=stock_url,
        symbol=ticker,
        time_in_force=tif,
        quantity=quantity,
        price=price,
        )
    
    # sometimes the sell_order comes back as a tuple, and sometimes not... so, fix it
    try:
        sell_order = sell_order[0]
    except Exception:
        sell_order = sell_order
        
    if sell_order == None:
        resp = "There was no response"
    elif sell_order.status_code == 201:
        resp = "Order Place Successfully at {}".format(sell_order.json()['price'])
    else:
        resp = "Something went wrong"
        
    return sell_order, resp



def buyStock_MKT(ticker, quantity, tif):
    """ Buy a Stock at the market price """
    
    stock_url = rh.get_quote(ticker)['instrument']
#     print(stock_url)
    buy_order = rh.place_market_buy_order(
        instrument_URL=stock_url,
        symbol=ticker,
        time_in_force=tif,
        quantity=quantity,
        )
    # sometimes the buy_order comes back as a tuple, and sometimes not... so, fix it
    try:
        buy_order = buy_order[0]
    except Exception:
        buy_order = buy_order
        
    if buy_order.status_code == 201:
        resp = "Order Placed Successfully at {}".format(buy_order.json()['price'])
    else:
        resp = "Something went wrong"
    return buy_order, resp



def sellStock_MKT(ticker, quantity, tif):
    """ Sell a Stock at the market price """
    
    if not login_response:
        print("We've entered a shadow zone")
#         rh = Robinhood()
#         login_resp = False
#         login_resp = rh.login(username=rh_user, password=rh_password, qr_code=rh_QR)
#         print(login_resp)
    else:
        print("Login Respoonse: {}".format(login_response))

    stock_url = rh.get_quote(ticker)['instrument']
#     print(stock_url)
    sell_order = rh.place_market_sell_order(
        instrument_URL=stock_url,
        symbol=ticker,
        time_in_force=tif,
        quantity=quantity,
        )
    
    # sometimes the sell_order comes back as a tuple, and sometimes not... so, fix it
    try:
        sell_order = sell_order[0]
    except Exception:
        sell_order = sell_order
    
    if sell_order == None:
        resp = "There was no response"
        pass
    elif sell_order.status_code == 401:
        resp = "Bad URL {}".format(sell_order.status_code)
        pass
    elif sell_order.status_code == 201:
        resp = "Order Place Successfully at {}".format(sell_order.json()['price'])
        pass
    else:
        resp = "Something else went wrong"
        pass
        
    return sell_order, resp


def get_RH_Price(ticker):
    stock_instrument = rh.instruments(ticker)[0]
    # Get a stock's quote
    stock_quote = rh.quote_data(ticker)
    # Market price
    return float(stock_quote['last_trade_price'])


def getPrices(tickers):
    """ Get stock prices for a list of tickers from Yahoo Finance, then IEX """
    prices = []

    for tick in tickers:
        # We're going to randomly choose the source, because... we cray
        rand = np.random.rand()

        url = 'https://finance.yahoo.com/quote/{}'.format(tick)
        session = requests_html.HTMLSession()
        resp = session.get(url)
        content = BeautifulSoup(resp.text, 'lxml')
        

        
        # Use Web Scrape, we'll prefer this 80% of the time
        if rand < 0.8:
            try:
                price = str(content).split('data-reactid="52"')[4].split('</span>')[0].replace('>','')
                price = float(price.replace(',',''))
            except Exception:
                # In case IEX fails use UniBit... may also be useful to compare(future)
                try:
                    security = Stock(tick, token=iex_token)
                    price = security.get_quote()['latestPrice']
                except Exception:
                    price = sp.getPricesRealTime(tick)['Realtime Stock price'][0]['price']

        # Use IEX Cloud 19.99% of the time:
        elif rand < 0.9999:           
            try:
                security = Stock(tick, token=iex_token)
                price = security.get_quote()['latestPrice']
            except Exception:
                # In case the Scrape fails use UniBit... may also be useful to compare(future)
                try:
                    price = str(content).split('data-reactid="52"')[4].split('</span>')[0].replace('>','')
                    price = float(price.replace(',',''))
                except Exception:
                    price = sp.getPricesRealTime(tick)['Realtime Stock price'][0]['price']
        # Use UniBit 0.1% of the time:
        else:
            try:
                price = sp.getPricesRealTime(tick)['Realtime Stock price'][0]['price']
            except Exception:
                # In case IEX and Unibit fails use Scrape... may also be useful to compare(future)                  
                try:
                    security = Stock(tick, token=iex_token)
                    price = security.get_quote()['latestPrice']
                except Exception:
                    price = str(content).split('data-reactid="52"')[4].split('</span>')[0].replace('>','')
                    price = float(price.replace(',',''))              
                                  
        prices.append(price)
        print(str(tick) + ":\t" + str(price))

    return prices

def killOpenOrders():
    """searches past 100 transactions and kills anything that's outstanding"""
    order_hist = rh.order_history()['results']
    output = []
    for i in range(100):
        if len(order_hist[i]['executions']) == 0 and (
            order_hist[i]['state'] =='queued' or order_hist[i]['state'] == 'confirmed'):
            output.append(order_hist[i])
            rh.cancel_order(order_hist[i]['id'])
    return output


def currentHoldings():
    """Queries Robinhood portfolio for current holdings
    Returns dictionary: Ticker: [starting trigger price, quantity, average buy price, last trade price]"""
    explore = rh.positions()
    current_holdings = {}
    for i in range(len(explore['results'])):
        if float(explore['results'][i]['quantity']) > 0:
            stock_instrument = explore['results'][i]['instrument']
            ticker = rh.security_tick(stock_instrument)
            latest = round(float(rh.get_quote(stock=ticker)['last_trade_price']),4)
            aveBuy = round(float(explore['results'][i]['average_buy_price']),4)
            quantity = round(float(explore['results'][i]['quantity']),1)
            start_trigger = round(float((0.3333 * aveBuy) + (0.6666 * latest)),4)
            print("Currently holding {} shares of {}".format(quantity, ticker))
            current_holdings.update({ticker: [start_trigger, quantity, aveBuy, latest]})
    return current_holdings
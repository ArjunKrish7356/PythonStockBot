import pandas as pd
import time
import ks_api_client
from ks_api_client import ks_api
import requests 
import os
from chart import *
import csv
import numpy as np

access_token =""
consumer_key =''
userid =''
password =''
symbol = 2094 

# https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_Cash_26_05_2023.txt

# Defining the host is optional and defaults to https://tradeapi.kotaksecurities.com/apim
# See configuration.py for a list of all supported configuration parameters.
client = ks_api.KSTradeApi(access_token =access_token, userid =userid , \
                consumer_key =consumer_key , ip = "127.0.0.1", app_id = "test")

# Get session for user
client.login(password = "Arjun@123")

#Generated session token
client.session_2fa(access_code = "1665")


df = pd.DataFrame()
global_stock=0 #Amount of stock can be bought
global_margin_utilised=0 #Margin utilised
global_price=0 #Price of stock
global_STOCK_INHAND=0
# ---------------------------------------------------------------------------------------------------------

def moving_average_crossover_strategy(data, short_window=20, long_window=50):
    # Calculate the short-term moving average
    ma_short = data['ltp'].tail(20).rolling(window=short_window).mean()

    # Calculate the long-term moving average
    ma_long = data['ltp'].tail(50).rolling(window=long_window).mean()

    # Check for buy signal
    if ma_short.iloc[-1] > ma_long.iloc[-1]:
        signal = 1
    # Check for sell signal
    elif ma_short.iloc[-1] < ma_long.iloc[-1]:
        signal = -1
    else:
        signal = 0

    return signal


def strategy():
    if check_enough_data('data.csv', 51):
        # Load the data from the CSV file
        data = pd.read_csv('data.csv')

        # Apply the moving average crossover strategy
        data = moving_average_crossover_strategy(data)
        return data
    else:
         return 0

def get_latest_signal(csv_file):
    data = pd.read_csv(csv_file)  # Read the CSV file into a DataFrame
    latest_signal = data['Signal'].iloc[-1]  # Retrieve the last value of the 'Signal' column
    return latest_signal

def check_enough_data(file_path, min_lines):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        line_count = sum(1 for _ in reader)
        if line_count >= min_lines:
            return True
        else:
            return False

def buy_order():
    global global_stock
    global global_STOCK_INHAND
    if check_enough_data('data.csv', 51):
        if global_margin_utilised == 0:
            if get_latest_signal('data.csv') == 1:
                
                 client.place_order(order_type="MIS", instrument_token=symbol, transaction_type="BUY",
                                    quantity=global_stock, price=0, disclosed_quantity=0, trigger_price=0,
                                    validity="GFD", variety="REGULAR", tag="string")
                 print(f"BUY ORDER PLACED FOR {global_stock}")
                 global_STOCK_INHAND=global_STOCK_INHAND+global_stock
                 print(global_STOCK_INHAND)
            else:
                print("No action taken")
        elif global_margin_utilised > 0:
            if get_latest_signal('data.csv') == -1:
                print("stock sold successfully")
                client.place_order(order_type="MIS", instrument_token=symbol, transaction_type="SELL",
                                   quantity=global_STOCK_INHAND, price=0, disclosed_quantity=0, trigger_price=0,
                                   validity="GFD", variety="REGULAR", tag="string")
                global_STOCK_INHAND=global_STOCK_INHAND-global_STOCK_INHAND
            else:
                print("No action taken")
    else:
        print("Not enough data to buy stock")

# #--------------------------------------------------------------------------------------------------------------------

 #main function enclosure  

def main():
    global df
    response = client.quote(instrument_token=symbol)  # create table and log data
    data = {
        'BD_last_traded_time': response['success'][0]['BD_last_traded_time'],
        'ltp': [response['success'][0]['ltp']],
        'last_trade_qty': [response['success'][0]['last_trade_qty']],
        'BD_TTQ': [response['success'][0]['BD_TTQ']],
        'Signal': strategy()
    }
    df = pd.DataFrame(data)
    
    df.to_csv('data.csv', mode='a', header=False, index=False)


        
#-------------------------------------------------------------------------------------------------------


#FUNCTIONS EXECUTED HERE




def cur_time():    #function to get current time
     current_time = time.time()
     current_time_string = time.ctime(current_time)
     print("Current time:", current_time_string)

def balance():
    global global_margin_utilised

    url_margin='https://tradeapi.kotaksecurities.com/apim/margin/1.0/margin'
    headers_margin={'accept':'application/json','consumerKey':consumer_key,'sessionToken': client.session_token, "Authorization":f"Bearer {access_token}"}
    res_margin=requests.get(url_margin,headers=headers_margin).json()  
    def show_balance(response):
         global global_margin_utilised

         cash_balance = response['Success']['equity'][0]['cash']['availableCashBalance']
         margin_available = response['Success']['equity'][0]['cash']['marginAvailable']
         global_margin_utilised = response['Success']['equity'][0]['cash']['marginUtilised']
         realized_pl = response['Success']['equity'][0]['cash']['realizedPL']
         
         print(f"Cash Balance: {cash_balance}")
         print(f"Margin Available: {margin_available}")
         print(f"Margin Utilized: {global_margin_utilised}")
         print(f"Realized P&L: {realized_pl}")
    show_balance(res_margin)

def stock():
    global global_stock
    url_margin='https://tradeapi.kotaksecurities.com/apim/margin/1.0/margin'
    headers_margin={'accept':'application/json','consumerKey':consumer_key,'sessionToken': client.session_token, "Authorization":f"Bearer {access_token}"}
    res_margin=requests.get(url_margin,headers=headers_margin).json()  
    def show_balance(response):
         cash_balance = response['Success']['equity'][0]['cash']['marginAvailable']
         return cash_balance
    def curr_balance():
        global global_stock
        response = client.quote(instrument_token=symbol)
        price = response['success'][0]['ltp']
        return float(price)
    val1=show_balance(res_margin)
    val2=curr_balance()
    global_stock=int(val1/val2)
    print(f"No. of stocks to buy: {global_stock}")

def stock_price():
    global global_price
    response = client.quote(instrument_token=symbol)
    global_price = response['success'][0]['ltp']
    stock_name = response['success'][0]['stk_name']
    print( f"{stock_name} ({symbol}) Stock Price: {global_price}")

#--------------------------------------------------------------------------------------------------------------------

# REPEAT FUNCTION
while True:
    main()  # Call the main function
    os.system('cls')
    print("DASHBOARD")
    cur_time()  # Call the current time function
    stock_price()  # Call the stock_price function
    balance()  # Call the balance function
    stock()  # Call the no_stock function 
    buy_order()  # Call the buy_order function
    # chart()
    print(f"global stock in hand{global_STOCK_INHAND}")
    
    time.sleep(10)  # Wait for 60 seconds (1 minute)


# ---------------------------------------------------------------------------------------------------------------




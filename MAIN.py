import csv
import threading
import time

class MarketData:
    def __init__(self,address:str):
        self.address=address
        self.file=open(address,'r')
        self.reader = csv.DictReader(self.file)
        self.order=False
        self.buyprice=0     #This buyprice and sell price is to determine my profit
        self.sellprice=0
        self.bema200=0
            
    def quotes(self):
            return next(self.reader)
        
    def buy(self):
            self.order=True
    def sell(self):
            self.order=False


def calculate_ema(values, n):
        if len(values) < n:
            raise ValueError("Insufficient data points to calculate EMA.")
        smoothing_factor = 2 / (n + 1)
        sma = sum(values[:n]) / n
        ema = (values[-1] - sma) * smoothing_factor + sma
        return ema


lock=threading.Lock()

def start(): 
    _200ltp=[]
    profit=0
    _macd=[]
    while True:
        with lock:
            try:
                ltp=float(client.quotes()['close'])
            except:
                continue
            if len(_200ltp)<200:                 #inserting values to the _200ltp array
                _200ltp.append(ltp)
            else:
                _200ltp.pop(0) 
                _200ltp.append(ltp)
                ema200=calculate_ema(_200ltp,200) #ema200
                ema26=calculate_ema(_200ltp,26)   #ema26
                ema12=calculate_ema(_200ltp,12)   #ema12
                macd=ema26-ema12
                if len(_macd)<9:                  #inserting values to the _macd array
                    _macd.append(macd)
                else:
                    _macd.pop(0)
                    _macd.append(macd)
                    
                if (ema200<ltp) and (client.order==False) and (len(_macd)>=9): #if ltp above ema and no stock in tradebook and signal_line can be made
                    signal_line=calculate_ema(_macd,9)      # create signla line ( current signal point)
            
                    if (macd<0) and (signal_line<0):
                        if(macd>signal_line):
                            try:
                                            # buy order
                                print(f"stock bought at : {ltp} at ema200 : {ema200} at profit :{profit}")
                                client.buy()
                                client.buyprice=ltp
                                client.bema200=ema200
                                tries=0
                            except e:
                                continue
                if(client.order==True):
                    tries+=1
                    if(ltp>client.buyprice*1.01):
                        client.sell()
                        print(f"stock sold at profit : {ltp} after {tries} minutes ")
                        profit+=ltp-client.buyprice
                    elif(tries>30):
                        client.sell()
                        print(f"stock sold at stoploss : {ltp} after {tries} minutes ")
                        profit+=ltp-client.buyprice
                    print(profit)
                    if((client.buyprice-client.bema200)>client.buyprice*0.01):
                        if(ltp<client.buyprice*0.998):
                            client.sell()
                            print(f"stock sold at stoploss2 : {ltp} after {tries} minutes ")
                            profit+=ltp-client.buyprice
                    else:
                        if(ltp<ema200*1.001):
                            client.sell()
                            print(f"stock sold at stoploss1 : {ltp} after {tries} minutes ")
                            profit+=ltp-client.buyprice
                        
                        
        time.sleep(0.001)              


def main():
    client = MarketData('VEDL-data.csv')  # you can replace the data you have with the csv file where you have stored your data
    client.start()

if __name__ == "__main__":
    main()

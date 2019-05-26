import pandas as pd
import numpy as np
import datetime as dt
from arch import arch_model
import matplotlib.pyplot as plt
import talib
import scipy
from scipy import optimize


class Position:
    def __init__(self,dt, price, volume):
        self.dt = dt
        self.price = price
        self.volume = volume



    dt=""
    code =""
    price = 0
    volume = 0



class Positons:
    long=[]
    short =[]


# df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\data\\TCFE收盘数据.xlsx")
# df['PCT_CHG'] = np.log(df['CLOSE']/df.PRE_CLOSE)
#
# start = dt.datetime(2000, 1, 1)
# end = dt.datetime(2014, 1, 1)
#
# returns = 100 * df.PCT_CHG.dropna()
# am = arch_model(returns)

def SMA(arr, n):
    output = np.zeros(len(arr))
    for i in np.arange(n-1, len(output)):
        output[i] = np.mean(arr[(i-n+1):(i+1)])
    output[0:(n-1)] = np.nan
    return output

def STD(arr, n, a=10):
    output = np.zeros(len(arr))
    temp = arr - SMA(arr, a)
    for i in np.arange(n+a-1, len(arr)):
        output[i] = np.sqrt(np.sum(temp[(i-n+1):(i+1)]**2)/n)
    output[0:(n+a-1)] = np.nan
    return output

# 统计回归的间隔
def statInterval(arr):
    countList = []
    i = 0
    tag = 1 if arr[0]>0 else 0
    for item in arr:
        if item > 0:
            if tag == 1:
                i += 1
            elif tag == 0:
                countList.append(i)
                i = 1
                tag = 1
        if item < 0 :
            if tag ==0:
                i += 1
            elif tag == 1:
                countList.append(i)
                i = 1
                tag = 0
    return countList

####


# 自适应均线
def MeanChange(arr, n):
    output = np.zeros(len(arr))
    for i in np.arange(n,len(arr)):
        output[i] = np.abs(arr[i]-arr[i-n])
    return output


def MeanVolatility(arr, n):
    output = np.zeros(len(arr))
    for i in np.arange(n,len(arr)):
        output[i] = np.sum(np.abs(arr[(i-n+1):i]-arr[(i-n):(i-1)]))
    return output


def SC(arr, n):
    meanC = MeanChange(arr,n)
    meanVol = MeanVolatility(arr,n)
    return (meanC/meanVol*(2/(2+1) - 2/(30+1)) + 2/(30+1))**2




def profitsCal(df,start,end,positionList,upper=0.02,lower=0.01, adds = 0.1, cutoff = 0.1):
    tradeList=[]
    buyList = []
    buypriceList = []
    sellList = []
    sellpriceList = []
    profitsList = []

    for i in np.arange(start, end):
        temppositionList = []
        for j in np.arange(len(positionList)):
            if df.close[j] < positionList[j].price - cutoff:
                profits = df.close[j] - positionList[j].price
                profitsList.append(profits)
            else:
                temppositionList.append(positionList[j])
        positionList = temppositionList

        if df.close[i]<df.KAMA[i-1] - lower and len(positionList) <= 10:
            if len(positionList) == 0 or (len(positionList) > 0 and df.close[i] < positionList[-1].price):
                buyList.append(i)
                position = Position(df.time[i], df.close[i], 1)
                positionList.append(position)
        elif df.close[i] > df.KAMA[i-1] + upper and len(positionList)>0:
            sellList.append(i)
            sellprice = df.close[i]
            sellposition = positionList.pop(0)
            profits = sellprice - sellposition.price
            profitsList.append(profits)
            if df.close[i] - df.KAMA[i-1] > upper+adds:
                sellList.append(i)
                sellprice = df.close[i]
                while len(positionList)>0:
                    sellposition = positionList.pop(0)
                    profits = sellprice - sellposition.price
                    profitsList.append(profits)
    # print(sum(profitsList))
    # print(len(profitsList))
    # print(len(buyList) - len(sellList))
    return profitsList, buypriceList, sellpriceList,sum(profitsList),positionList




















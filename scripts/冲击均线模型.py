import numpy as np
import pandas as pd
from scripts.波动率计算 import *

df1 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113009广汽转债")
df2 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113021中信转债")
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="110053苏银转债")


df3 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="127012招路转债")
df4 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113011光大转债")
df5 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113013国君转债")
df6 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="110046圆通转债")
df7 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="110051中天转债")

df['Mean'] = SMA(df.close.values, 30)
df['Std'] = STD(df.close.values, 30)
a = 60
df['Mean'] = SMA(df.close.values, a)
df['Std'] = STD(df.close.values, 20, a)
df['KAMA'] = talib.KAMA(df.close, 30)
df1['KAMA'] = talib.KAMA(df1.close, 30)
df2 = df2.fillna(method='ffill')
df2['KAMA'] = talib.KAMA(df2.close, 20)
df3['KAMA'] = talib.KAMA(df3.close, 20)
df4['KAMA'] = talib.KAMA(df4.close, 20)
df5['KAMA'] = talib.KAMA(df5.close, 20)
df6['KAMA'] = talib.KAMA(df6.close, 20)
df7['KAMA'] = talib.KAMA(df7.close, 20)

def profitsCal(df,start,end,positionList,upper=0.02,lower=0.01, adds = 0.1, cutoff = 0.1):
    buypriceList = []
    yieldList = []
    for i in np.arange(1,df.shape[0]):
        if len(buypriceList) > 0 and (df.high[i] >= buypriceList[0] + 0.02 or df.high[i-1] >= buypriceList[0] + 0.02):
            yieldList.append(0.015)
            buypriceList.pop(0)
        # if len(buypriceList) > 0 and df.high[i] == buypriceList[0] + 0.03:
        #     yieldList.append(0.015)
        #     buypriceList.pop(0)
        # if len(buypriceList) > 0 and df.high[i] == buypriceList[0] + 0.02:
        #     yieldList.append(-0.005)
        #     buypriceList.pop(0)
        if len(buypriceList) > 0 and df.low[i] <= df.high[i] - 0.02:
            yieldList.append(max(df.high[i]-buypriceList[0]-0.02,df.high[i-1]-buypriceList[0]-0.02))
            buypriceList.pop(0)

        if df.high[i] >= df.KAMA[i]-0.02 and df.close[i-1] < df.KAMA[i-1]: # 前一分钟的收盘价在均值一下，这一分钟的最高价在均值以上
            if buypriceList.__len__() == 0:
                buypriceList.append(df.KAMA[i]-0.015)
    return yieldList

def Cal(df,start,end,positionList,upper=0.02,lower=0.01, adds = 0.1, cutoff = 0.1):
    yieldList = []
    for i in np.arange(100, df.shape[0]):
        if df.close[i-1] < df.KAMA[i-1]:
            if df.high[i] >= df.KAMA[i] + 0.01: # 前一分钟的收盘价在均值一下，这一分钟的最高价在均值以上
                yieldList.append(0.01)
            if df.high[i] > df.KAMA[i] - 0.02 and df.high[i] < df.KAMA[i] + 0.01:
                yieldList.append(-0.01)
    return yieldList


yieldList = profitsCal(df2,100,4000,[])
print(len(yieldList))
print(sum(yieldList))

yieldList = profitsCal(df1,100,4000,[])
print(len(yieldList))
print(sum(yieldList))

yieldList = profitsCal(df,100,4000,[])
print(len(yieldList))
print(sum(yieldList))

yieldList = profitsCal(df3,100,4000,[])
print(len(yieldList))
print(sum(yieldList))

yieldList = profitsCal(df4,100,4000,[])
print(len(yieldList))
print(sum(yieldList))

yieldList = profitsCal(df5,100,4000,[])
print(len(yieldList))
print(sum(yieldList))

yieldList = profitsCal(df6,100,4000,[])
print(len(yieldList))
print(sum(yieldList))

yieldList = profitsCal(df7,100,4000,[])
print(len(yieldList))
print(sum(yieldList))


##################2019年5月27日16:58:51
df = df4
df['KAMA'] = talib.KAMA(df.close, 20)
temp = (df.low - df.KAMA.shift(1)).dropna().values
notes = []
su = []
for item in temp:
    if item < 0:
       su.append(item)
    else:
        if su.__len__()>0:
            notes.append(min(su))
            su = []

#### 静态分布情形
-0.2 # 回复状态下最好点位 收益25.2

plt.hist(notes, 100)
plt.show()

re = []
for i in np.arange(0, -1, -0.01):
    re.append(sum(notes < i)*(-i))




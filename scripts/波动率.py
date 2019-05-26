import pandas as pd
import numpy as np
import datetime as dt
from arch import arch_model
import matplotlib.pyplot as plt
import talib
import matplotlib
import scipy.stats as stat

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False

df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\data\\TCFE收盘数据.xlsx")
df['PCT_CHG'] = np.log(df['CLOSE']/df.PRE_CLOSE)

start = dt.datetime(2000, 1, 1)
end = dt.datetime(2014, 1, 1)

returns = 100 * df.PCT_CHG.dropna()
am = arch_model(returns)

def SMA(arr, n):
    output = np.zeros(len(arr))
    for i in np.arange(n-1, len(output)):
        output[i] = arr[(i-n+1):(i+1)].mean()
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

res = am.fit()
res.plot()

plt.plot(df.CLOSE)

plt.plot(res._volatility)
plt.twinx()
plt.plot(df.CLOSE)
plt.show()

notes = 0
for i in np.where(returns>res._volatility)[0]:
    if df.CLOSE[i] - min(df.CLOSE[i:(i+5)]) > 0 and i < 980:
        notes += 1


####
# 转债数据
df = pd.read_excel("C:\\Users\\l_cry\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113009广汽转债")
df['Mean'] = SMA(df.close.values, 10)
df['Std'] = STD(df.close.values, 10)

plt.plot(df.time, df.Mean+2*df.Std)
plt.plot(df.time, df.Mean-2*df.Std)
plt.plot(df.time, df.close)
plt.show()

a = 30
df['Mean'] = SMA(df.close.values, a)
df['Std'] = STD(df.close.values, 20, a)
buyList = []
sellList = []
yieldList = []
tag = 0
for i in np.arange(100,df.shape[0]):
    if df.close[i]<df.Mean[i-1]-0.26:
        if tag == 0:
            sellList.append(i)
            price1 = df.close[i]
            tag = 1
    if df.close[i]>df.Mean[i-1] + 0.26:
        if tag == 1:
            buyList.append(i)
            tag = 0
            yieldList.append(df.close[i] - price1)

sum(yieldList)

df['KAMA'] = talib.KAMA(df.close.values, 30)
buyList = []
sellList = []
yieldList = []
tag = 0
for i in np.arange(100,df.shape[0]):
    if df.close[i] < df.KAMA[i-1]-1.4*0.26:
        if tag == 0:
            sellList.append(i)
            price1 = df.close[i]
            tag = 1
    if df.close[i] > df.KAMA[i-1] + 1.4*0.26:
        if tag == 1:
            buyList.append(i)
            tag = 0
            yieldList.append(df.close[i] - price1-0.06)

sum(yieldList)

countList = statInterval((df.close - df.KAMA.shift(1)).dropna().values)

# 偏离累计时长分布图
plt.hist(countList,20,density=True)
plt.xlabel("偏离趋势持续时长")
plt.ylabel("频率")
plt.title("偏离累计时长分布图")
plt.show()

countSMAList = statInterval((df.close - df.Mean.shift(1)).dropna().values)
plt.hist(countSMAList,20,density=True)
plt.xlabel("偏离趋势持续时长")
plt.ylabel("频率")
plt.title("移动平均线偏离累计时长分布图")
plt.show()



plt.hist((df.close - df.KAMA.shift(1)).dropna().values, 40, density=True)
plt.xlabel("价格偏离趋势范围（自适应均线）")
plt.ylabel("密度")
plt.title("价格偏离趋势的分布")
plt.show()

plt.hist((df.close - df.Mean.shift(1)).dropna().values, 40, density=True)
plt.xlabel("价格偏离趋势范围（移动平均线）")
plt.ylabel("密度")
plt.title("价格偏离趋势的分布")
plt.show()

temp = (df.close - df.KAMA.shift(1)).dropna().values
stat.kstest((temp-temp.mean())/temp.std(),cdf='norm')


temp1 = (df.close - df.Mean.shift(1)).dropna().values
stat.kstest((temp1-temp1.mean())/temp1.std(), cdf='norm')


x = 0.5
re = []
for x in np.arange(0,1,0.01):
    re.append(sum(temp>x)*x/(temp[(temp-x)>0]-x).max())
max(re)

re1 = []
for x in np.arange(0,1,0.01):
    re1.append(sum(temp1>x)*x/(temp1[(temp1-x)>0]-x).max())
max(re1)

plt.plot(df.close)
plt.plot(df.Mean,'y-')
plt.show()


plt.plot(df.close)
plt.plot(df.close-df.KAMA,'y-')
plt.show()

plt.xticks(rotation=45)
plt.plot(df.time,df.close)
plt.ylabel("价格")
plt.twinx()
plt.plot(df.time[sellList], np.cumsum(yieldList), 'y-')
plt.ylabel("收益")
plt.title("累积收益（移动平均线）")
plt.show()


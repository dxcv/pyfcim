import pandas as pd
import matplotlib.pyplot as plt
import talib
import numpy as np
import matplotlib


matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False
df = pd.read_excel("C:\\Users\\l_cry\\Desktop\\113011光大转债tick数据.xlsx")

df.time = [pd.to_datetime("20190524 %s" % df.time[i].strftime("%H:%M:%S")) for i in range(df.shape[0])]
df.index = df.time

dfMin = df.price.resample('min').last().fillna(method='ffill').to_frame()

df['Min'] = df.time.apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))



dfMin['time'] = dfMin.index.values
dfMin['Min'] = dfMin.time.apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
dfMin['KAMA'] = talib.KAMA(dfMin.price,20)
dfMin['price_shift1'] = dfMin.price.shift(1)
dfMin['KAMA_shift1'] = dfMin.KAMA.shift(1)



dfT = df.merge(dfMin,'left',on='Min',left_index=True)


dfT['PriceDiff'] = dfT.price_x - dfT.KAMA_shift1
dfT['KAMADiff'] = dfT.KAMA - dfT.KAMA_shift1


plt.hist(dfT.PriceDiff.dropna(),100)
plt.title('价格相对于均线偏离分布')
plt.show()

plt.hist(dfT.KAMADiff.dropna(),100)
plt.title('均线相对自身变动分布')
plt.show()

plt.plot(dfT.time_x, dfT.KAMA)
plt.plot(dfT.time_x, dfT.price_x)
plt.xlabel('time')
plt.ylabel('price')
plt.legend(['KAMA','price'])
plt.title('tick data')
plt.show()
### celue

plt.plot(dfT.PriceDiff,dfT.KAMADiff,'.')
plt.xlabel('价格变动')
plt.ylabel('均线变动')
plt.show()


np.corrcoef(dfT.PriceDiff,dfT.KAMADiff)


dfT[['PriceDiff','KAMADiff']].dropna().corr()

plt.hist(dfMin.price- dfMin.price.shift(1),100)
plt.show()

plt.plot(dfMin.price- dfMin.price.shift(1))
plt.show()

th = 0.01
temp = -(dfMin.price- dfMin.price.shift(1)).dropna().values
newList = []
n00,n01,n10,n11 = 0,0,0,0
for curr, nex in zip(temp[:-1],temp[1:]):
    if curr > th and nex > th:
        n11 += 1
    if curr > th >= nex:
        n10 += 1
    if curr <= th < nex:
        n01 += 1
    if curr <= th and nex <= th:
        n00 += 1

pi01 = n01/(n00+n01)
pi11 = n11/(n10+n11)
pi2 = (n01+n11)/(n00+n01+n10+n11)

2*(n00*np.log(1-pi01)+n01*np.log(pi01)+n10*np.log(1-pi11)+n11*np.log(pi11)) - 2*((n00+n10)*np.log(1-pi2)+(n01+n11)*np.log(pi2))





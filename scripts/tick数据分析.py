import pandas as pd
import matplotlib.pyplot as plt
import talib
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\113011光大转债tick数据.xlsx")

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


dfT['PriceDiff'] = dfT.price_x - dfT.price_shift1
dfT['KAMADiff'] = dfT.price_x - dfT.KAMA_shift1

plt.hist(dfT.PriceDiff.dropna(),100)
plt.show()

plt.hist(dfT.KAMADiff.dropna(),100)
plt.show()

plt.plot(dfT.time_x, dfT.KAMA)
plt.plot(dfT.time_x, dfT.price_x)
plt.show()
### celue









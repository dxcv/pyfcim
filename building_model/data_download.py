#%%
import numpy as np
import tensorflow as tf
import pandas as pd
from WindPy import *
w.start()
#%%
code = "TF.CFE"
all_factorlist = "adtm,atr,bbi,bbiboll,bias,boll,cci,cdp,dma,dmi,dpo,env,expma,kdj,slowkd,ma,macd,mike,mtm,priceosc,pvt,rc,roc,rsi,sar,si"
factorlist = all_factorlist.upper().replace(' ','').split(",")
datelist = list(w.tdays('2015-01-07', '2018-11-20', "Period=D", usedf=False).Times)
data =  w.wsd(code, ['open', 'high', 'low', 'close', 'pct_chg']+factorlist, '2016-01-07', '2016-01-07')
data = pd.DataFrame(data.Data, columns=data.Times,index=data.Fields).T

for dt in datelist:
    # 受限于单次提取数据的限制，这里分多次提取
    bar_datetime_str = dt.strftime('%Y-%m-%d')
    data_append =  w.wsd(code, ['open', 'high', 'low', 'close', 'pct_chg']+factorlist, bar_datetime_str, bar_datetime_str)
    data_append = pd.DataFrame(data_append.Data, columns=data_append.Times, index=data_append.Fields).T
    data = data.append(data_append)
    print(bar_datetime_str," save done!")

# data.index = data.index.strftime('%Y%m%d')
data.to_csv('C:/Users/l_cry/Desktop/data/MLtimingdata160107_181120TFCFE.csv')
print("Data save done!")





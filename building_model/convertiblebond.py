#%%
import pandas as pd
from WindPy import *
w.start()
#%%
tradeCalendar = w.tdays("2018-01-26", "2019-02-26", "")

re_List = []
re_List1 = []
for Date in tradeCalendar.Times:
    error, df = w.wset("indexconstituent", "date=%s;windcode=000832.CSI" % Date.strftime("%Y-%m-%d"),usedf=True)
    # error, df = w.wset("sectorconstituent","date=%s;sectorid=a101020600000000" % Date.strftime("%Y-%m-%d"), usedf=True)
    if error == 0:
        code_list = ','.join(df.wind_code.values)
        error1, data = w.wss(code_list, "convpremiumratio,outstandingbalance,dirtyprice", "tradeDate=%s" % Date.strftime("%Y%m%d"),usedf=True)
        if error1 == 0:
            re_List.append([Date.strftime("%Y-%m-%d"), data.CONVPREMIUMRATIO.dropna().mean()])
            re_List1.append([Date.strftime("%Y-%m-%d"), sum(df.i_weight.values * data.CONVPREMIUMRATIO.values/100)])

#%%
df_convpremiumratio = pd.DataFrame(re_List, columns=['date', 'convpremiumratio'])
df_convpremiumratio1 = pd.DataFrame(re_List1, columns=['date', 'convpremiumratio'])


























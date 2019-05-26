#%%
from WindPy import *
w.start()
import pandas as pd
#%%
index = []
dt = '2019-03-13'
for dt in w.tdays("2018-2-12", "2019-03-14").Data[0]:
    error, df = w.wset("indexconstituent","date=%s;windcode=000832.CSI" % dt.strftime("%Y-%m-%d"), usedf=True)
    output = []
    for code in df.wind_code:
        re = w.wsd(code, "close,convprice,cb_pq_stockclose,pq_close", dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d"), "bondPriceType=4").Data
        output.append([re[0][0],re[1][0],re[2][0],re[3][0],df[df.wind_code==code].i_weight.values[0]])
    output = pd.DataFrame(output,columns=['close','convprice','cb_pq_stockclose','pq_close','i_weight'])
    a = sum((output.cb_pq_stockclose/output.convprice)*output.i_weight)
    b = sum((output.pq_close*output.i_weight/100))
    print(dt.strftime("%Y-%m-%d"))
    index.append([dt, a, b])

index_df = pd.DataFrame(index, columns=('datetime','平价','总价'))
index_df.to_excel("C:\\Users\\l_cry\\Desktop\\data\\转债平价2.xlsx")
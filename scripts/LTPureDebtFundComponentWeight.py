#%%
import pandas as pd
import numpy as np
from WindPy import *
from numba import jit, prange
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
import pymssql
from scipy import optimize
from matplotlib.font_manager import FontProperties
import matplotlib
from sqlalchemy import create_engine
#font = FontProperties(fname='/Library/Fonts/Songti.ttc')
#指定默认字体
#matplotlib.rcParams['font.sans-serif'] = ['SimHei']
#matplotlib.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
#matplotlib.rcParams['axes.unicode_minus'] = False

tz_sh = pytz.timezone('Asia/Shanghai')
# 启动wind
w.start()

dt = datetime.now()

# 长债基金指数分析
error_code,df = w.wsd("000832.CSI,885008.WI,885009.WI,CBA00351.CS,CBA02001.CS", "pct_chg", datetime(dt.year-4,dt.month,dt.day).strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d"), usedf=True) # 起止时间
# '中证转债000832.CSI','货币市场基金指数885009.WI','中债总财富(7-10年)指数CBA00351.CS','中债企业债总财富(总值)指数CBA02001.CS'
# '长期纯债型基金指数885008.WI'
#df.index = date2num(df.index)
df['date'] = df.index
input_X = df[['000832.CSI', '885009.WI', 'CBA00351.CS', 'CBA02001.CS']].values
input_y = df[['885008.WI']].values.reshape(-1,1)

#%%
@jit(nopython=True, parallel=True)
def ex(X, y, Date, n):
    re_list = np.zeros((X.shape[0]-n, 6))
    for i in prange(n,X.shape[0],1):
        coff,fitness = iter_cal(X[(i-n):i,:],
                 y[(i-n):i,:],np.array([0.2,0.2,0.2,0.2]).reshape(-1,1))
        re_list[i-n] = np.array([Date[i], coff[0][0], coff[1][0], coff[2][0], coff[3][0], fitness])
        print(i)
    # pool.close()
    # pool.join()
    return re_list

# @jit(nopython=True, parallel=True)
def ex1(X, y, Date, n):
    cons = ({'type': 'ineq', 'fun': lambda x: x[0]},
            {'type': 'ineq', 'fun': lambda x: x[1]},
            {'type': 'ineq', 'fun': lambda x: 0.7 - x[1]},
            {'type': 'ineq', 'fun': lambda x: x[2]},
            {'type': 'ineq', 'fun': lambda x: x[3]},
            {'type': 'ineq', 'fun': lambda x: 1.4 - (x[0] + x[1] + x[2] + x[3])})
    re_list = [0 for i in range(X.shape[0]-n)]
    j=0
    for i in prange(n, X.shape[0], 1):
        fitness = lambda params: ((y[(i-n):i,:] - X[(i-n):i,:].dot(params.reshape(-1, 1))).T).dot(y[(i-n):i,:] - X[(i-n):i,:].dot(params.reshape(-1, 1)))[0, 0]
        res = optimize.minimize(fitness, np.array([0.2,0.2,0.2,0.2]), method='SLSQP', constraints=cons)
        re_list[j] = [Date[i], res.x[0], res.x[1], res.x[2], res.x[3], res.fun]
        j += 1
        print(i)
    return re_list


@jit(nopython=True)
def gradint_cal(X,y,params,M=20):
    gradint = -X.T.dot(y-X.dot(params))
    for i in range(len(params)):
        if params[i,0]<0:
            gradint[i,0] += -2*M
        if params[i,0]>1:
            gradint[i,0] += 2*M
    if np.sum(params)>1:
        gradint += M
    #gradint[gradint>2]=2
    #gradint[gradint<-2]=-2
    return -gradint

@jit(nopython=True)
def iter_cal(X,y,params,a=0.001,n=50000,M=20):
    i = 0
    fitness_1 = 0
    fitness = ((y - X.dot(params)).T).dot(y - X.dot(params))[0, 0] + M * (
                max(params.sum(axis=0)[0] - 1, 0) + max(-params[0, 0], 0)
                + max(-params[1, 0], 0) + max(-params[2, 0], 0) + max(-params[3, 0], 0))
    gradint = gradint_cal(X, y, params)
    params += a * gradint
    while i < n and abs(fitness-fitness_1)>0.00000001:
        fitness_1 = fitness
        fitness = ((y - X.dot(params)).T).dot(y - X.dot(params))[0,0]+M*(max(params.sum(axis=0)[0]-1,0)+max(-params[0,0],0)
                                                               + max(-params[1, 0], 0)+max(-params[2,0],0)+max(-params[3,0],0))
        params += a * gradint_cal(X, y, params)
        i += 1
    return params,fitness


#%%
re_list = ex1(input_X,input_y,df['date'].values,20)
#%%
# re_list1 = ex(input_X,input_y,df['date'].values,20)
#%%
engine_InvestSystem = create_engine('mssql+pyodbc://bond:bond@10.28.7.43:1433/InvestSystem?driver=SQL+Server')
conn_43_InvestSystem = pymssql.connect(host = "10.28.7.43",user = "bond",password = 'bond',database = "InvestSystem")
cur = conn_43_InvestSystem.cursor()
sql = "TRUNCATE table LTPureDebtFundComponentWeight"
cur.execute(sql)
conn_43_InvestSystem.commit()
cur.close()
df2 = pd.DataFrame(re_list,columns=('date', '000832.CSI', '885009.WI', 'CBA00351.CS', 'CBA02001.CS', 'fitness'))

df2.to_sql("LTPureDebtFundComponentWeight",engine_InvestSystem,index=False, if_exists='append')


# df2 = pd.DataFrame(re_list,columns=('日期','中证转债000832.CSI','货币市场基金指数885009.WI',
#                                '中债总财富(7-10年)指数CBA00351.CS','中债企业债总财富(总值)指数CBA02001.CS','fitness'))
#
#
#
# #df2['日期'] = df2['日期'].apply(lambda x: num2date(x,tz=tz_sh)-datetime.timedelta(hours=8))
# plt.figure(figsize=(20,10))
# plt.plot(df2['日期'],df2['中证转债000832.CSI'])
# plt.plot(df2['日期'],df2['货币市场基金指数885009.WI'])
# plt.plot(df2['日期'],df2['中债总财富(7-10年)指数CBA00351.CS'])
# plt.plot(df2['日期'],df2['中债企业债总财富(总值)指数CBA02001.CS'])
# plt.legend(['中证转债000832.CSI','货币市场基金指数885009.WI',
#                                    '中债总财富(7-10年)指数CBA00351.CS','中债企业债总财富(总值)指数CBA02001.CS'])


# plt.show()


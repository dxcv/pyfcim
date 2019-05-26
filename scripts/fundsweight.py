#%%
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from WindPy import *
from scipy import optimize
import matplotlib.pyplot as plt

w.start()
#%%
error_code,df = w.wsd("885000.WI,882001.WI,882002.WI,882003.WI,882004.WI,882005.WI,882006.WI,882007.WI,882008.WI,882009.WI,882010.WI,882011.WI", "pct_chg", "2015-01-18", "2019-02-16", usedf=True)
#%%
input_X = df[['882001.WI','882002.WI','882003.WI','882004.WI','882005.WI','882006.WI','882007.WI','882008.WI','882009.WI','882010.WI','882011.WI']].values
input_y = df[['885000.WI']].values.reshape(-1,1)
#%%
def ex1(X, y, Date, n):
    cons=({'type': 'ineq', 'fun': lambda x: x[0]},
          {'type': 'ineq', 'fun': lambda x: x[1]},
          {'type': 'ineq', 'fun': lambda x: x[2]},
          {'type': 'ineq', 'fun': lambda x: x[3]},
          {'type': 'ineq', 'fun': lambda x: x[4]},
          {'type': 'ineq', 'fun': lambda x: x[5]},
          {'type': 'ineq', 'fun': lambda x: x[6]},
          {'type': 'ineq', 'fun': lambda x: x[7]},
          {'type': 'ineq', 'fun': lambda x: x[8]},
          {'type': 'ineq', 'fun': lambda x: x[9]},
          {'type': 'ineq', 'fun': lambda x: x[10]},
          {'type': 'ineq', 'fun': lambda x: 1 - sum(x)})
    re_list =[0 for j in range(X.shape[0] - n)]
    j = 0
    for i in range(n, X.shape[0], 1):
        fitness = lambda params: ((y[(i-n):i,:] - X[(i-n):i,:].dot(params.reshape(-1, 1))).T).dot(y[(i-n):i,:] - X[(i-n):i,:].dot(params.reshape(-1, 1)))[0, 0] + sum(params)
        res = optimize.minimize(fitness, np.zeros(11)+0.05, method='SLSQP', constraints=cons)
        re_list[j] = list(res.x)
        j += 1
        print(i)
    return re_list

re_list = ex1(input_X,input_y,df.index.values,90)

#%%
df2 = pd.DataFrame(re_list,columns=('能源882001.WI','材料882002.WI','工业882003.WI',
                                    '可选消费882004.WI','日常消费882005.WI','医疗保健882006.WI','金融882007.WI',
                                    '信息技术882008.WI','电信服务882009.WI','公用事业882010.WI','房地产882011.WI'))
df2 = df2.applymap(lambda x: x if x >= 0.01 else 0)
df2['Date'] = df.index[90:]

#%%
plt.figure(figsize=(20,10))
plt.plot(df2['Date'],df2['882001.WI'])
plt.plot(df2['Date'],df2['货币市场基金指数885009.WI'])
plt.plot(df2['Date'],df2['中债总财富(7-10年)指数CBA00351.CS'])
plt.plot(df2['Date'],df2['中债企业债总财富(总值)指数CBA02001.CS'])
plt.legend(['中证转债000832.CSI','货币市场基金指数885009.WI',
                                   '中债总财富(7-10年)指数CBA00351.CS','中债企业债总财富(总值)指数CBA02001.CS'])

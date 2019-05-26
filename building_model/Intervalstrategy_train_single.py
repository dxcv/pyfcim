#%%
import sys
import pandas as pd
from sklearn import preprocessing
import numpy as np
from sklearn.decomposition import PCA
from building_model.Intervalstrategy_research import Intervalstrategy
from datetime import datetime
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
import matplotlib.pyplot as plt
import keras
#%%
data = pd.read_csv('C:/Users/l_cry/Desktop/data/MLtimingdata150107_181120TFCFE.csv')
data.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
data = data.fillna(method="ffill", axis=0)
data['HIGH1'] = data.HIGH.shift(-1)
data['HIGH2'] = data.HIGH.shift(-2)
data['HIGH3'] = data.HIGH.shift(-3)
data['HIGH4'] = data.HIGH.shift(-4)
data['HIGH5'] = data.HIGH.shift(-5)
data['HIGH6'] = data.HIGH.shift(-6)
data['HIGH7'] = data.HIGH.shift(-7)
data['maxHigh'] = data[['HIGH1', 'HIGH2', 'HIGH3', 'HIGH4', 'HIGH5', 'HIGH6']].max(axis=1)
data['HIGH_CHG'] = np.log(data['maxHigh']/data.CLOSE)*100
data['CLOSE7'] = data.CLOSE.shift(-7)
data['CLOSE1'] = data.CLOSE.shift(-1)
data['CLOSE_CHG_7'] = np.log(data.CLOSE7/data.CLOSE)*100
data['CLOSE_CHG'] = np.log(data.PCT_CHG/100+1)*100
data['CLOSE_CHG_1'] = np.log(data.CLOSE1/data.CLOSE)*100
data['LOW1'] = data.LOW.shift(-1)
data['LOW2'] = data.LOW.shift(-2)
data['LOW3'] = data.LOW.shift(-3)
data['LOW4'] = data.LOW.shift(-4)
data['LOW5'] = data.LOW.shift(-5)
data['LOW6'] = data.LOW.shift(-6)
data['minLOW'] = data[['LOW1','LOW2','LOW3','LOW4','LOW5','LOW6']].max(axis=1)
data['LOW_CHG'] = np.log(data['minLOW']/data.CLOSE)*100
data = data[data.CLOSE_CHG_7.notnull()].reset_index(drop=True)
#all_factorlist = "atr,bias,cci,dma,dmi,dpo,macd,mtm,priceosc,roc,rsi,sar,si"
all_factorlist = "PCT_CHG,atr,bias,dma,dmi,dpo,macd,mtm,priceosc,roc,rsi,sar,si"
factorlist = all_factorlist.upper().replace(' ', '').split(",")
datelist = data['date']
# 定义常量
days = 100
time_step = 1
data.head(10)

#%%
interstra = Intervalstrategy(7)
pnl = pd.DataFrame(datelist)
pnl['y'] = 0.0
pnl['yhat_lstm'] = 0.0
pnl['yhat_lstm_0'] = np.nan
pnl['yhat_lstm_1'] = np.nan
pnl['yhat_lstm_2'] = np.nan
valid_num = 150

X = data.loc[:, factorlist]
# y_raw = data.loc[j - days + 1: j, 'PCT_CHG']
# y_raw = data.loc[:, 'CLOSE_CHG_1']
y_raw = data.loc[:, 'CLOSE_CHG_7']
# 延长样本
# X = model.loc[:j-1, 'ADTM':'SI']
# y_raw = model.loc[1:j-1, 'PCT_CHG']
scaler = preprocessing.StandardScaler().fit(X)
X = scaler.transform(X)
quantile_30 = y_raw.quantile(0.3)
quantile_70 = y_raw.quantile(0.7)
fileshx = "CLOSE_CHG_valid150_layers3-"+datetime.now().strftime("%Y%m%d%H%M%S")+"-single"

def _get_label(x):
    if x >= 0:
        return 1
    else:
        return 0

def _get_label_3(x):
        if x>=quantile_70:
            return 2
        elif x>=quantile_30:
            return 1
        else:
            return 0

y = y_raw.apply(lambda x: _get_label_3(x)).values

# 主成分分析
# pca = PCA(n_components=7)
# pca.fit(X)
# X = pca.fit_transform(X)

# 转变数据类型
train_x, train_y, valid_x, valid_y = interstra.transform_data(X, y, time_step, valid_num)

#%%
# 模型训练和预测
# interstra.train_lstm(train_x, train_y, valid_x, valid_y, "./tmp/"+fileshx, epochs=200)
# predict2 = interstra.prediction(valid_x)

# ## 结果输出
# pnl.loc[-valid_num:, 'y'] = data.loc[-valid_num:, 'CLOSE_CHG_1']
# pnl['yhat_lstm'].iloc[-valid_num:] = np.argmax(predict2, axis=1)
# pnl['yhat_lstm_0'].iloc[-valid_num:] = predict2[:, 0]
# pnl['yhat_lstm_1'].iloc[-valid_num:] = predict2[:, 1]
# pnl['yhat_lstm_2'].iloc[-valid_num:] = predict2[:, 2]
# # print(date, metrics.accuracy_score(y[time_step - 1:], sample_yhat - 1), predict2)

# # pnl = pnl.loc[days + 1:, ]
# pnl.set_index(["date"], inplace=True)
# pnl.iloc[-valid_num:,:].to_excel("../data/"+fileshx+".xlsx")
# #interstra.savemodel("./"+fileshx+".h5")
# print('Done!')

#%%

from keras.utils import np_utils
train_x = train_x.reshape((train_x.shape[0], 1, train_x.shape[1]))
valid_x = valid_x.reshape((valid_x.shape[0], 1, valid_x.shape[1]))

model = Sequential()
model.add(LSTM(32, input_shape=(train_x.shape[1], train_x.shape[2])))
# model.add(Dense(train_y.shape[1], activation='softmax'))
model.add(Dense(1))
model.compile(loss='mae', optimizer='adam')
# model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(train_x, y_raw[:-valid_num], nb_epoch=200, batch_size=1, verbose=2, validation_data=(valid_x,  y_raw[-valid_num:]))
model.save("./"+fileshx+".h5")

#%%
predict1 = model.predict(train_x,batch_size=32)
predict2 = model.predict(valid_x,batch_size=32)
#%%
# print(np.hstack(([[1,2],[3,3]],[[3,4],[5,8]])))
# print(predict2)
mat1 = np.hstack((predict1,y_raw[:-valid_num].values.reshape(-1,1)))
mat2 = np.hstack((predict2,y_raw[-valid_num:].values.reshape(150,1)))
#%%
mat1 = mat1/100+1
mat2 = mat2/100+1
print(mat1.cumprod(axis=0))
print(mat2.cumprod(axis=0))
#%%
plt.plot(mat2[:,0])
#%%
plt.plot(mat2[:,1])
#%% 

model = keras.models.load_model("./"+fileshx+".h5")
model.predict(valid_x, batch_size=32)






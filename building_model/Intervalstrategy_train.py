
import sys
sys.path.append("../")
import pandas as pd
from sklearn import preprocessing
import numpy as np
from sklearn.decomposition import PCA
from building_model.Intervalstrategy_research import Intervalstrategy


data = pd.read_csv('C:/Users/l_cry/Desktop/data/MLtimingdata160107_180928.csv')
data.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
data = data.fillna(method="ffill", axis=0)
data['HIGH1'] = data.HIGH.shift(-1)
data['HIGH2'] = data.HIGH.shift(-2)
data['HIGH3'] = data.HIGH.shift(-3)
data['HIGH4'] = data.HIGH.shift(-4)
data['HIGH5'] = data.HIGH.shift(-5)
data['HIGH6'] = data.HIGH.shift(-6)
data['HIGH7'] = data.HIGH.shift(-7)
data['maxHigh'] = data[['HIGH', 'HIGH1', 'HIGH2', 'HIGH3', 'HIGH4', 'HIGH5', 'HIGH6']].max(axis=1)
data['HIGH_CHG'] = np.log(data['maxHigh']/data.CLOSE.shift(1))*100
data['CLOSE7'] = data.CLOSE.shift(-7)
data['CLOSE1'] = data.CLOSE.shift(-1)
data['CLOSE_CHG_7'] = np.log(data.CLOSE7/data.CLOSE.shift(1))*100
data['CLOSE_CHG_1'] = np.log(data.CLOSE1/data.CLOSE.shift(1))*100
data['LOW1'] = data.LOW.shift(-1)
data['LOW2'] = data.LOW.shift(-2)
data['LOW3'] = data.LOW.shift(-3)
data['LOW4'] = data.LOW.shift(-4)
data['LOW5'] = data.LOW.shift(-5)
data['LOW6'] = data.LOW.shift(-6)
data['minLOW'] = data[['LOW','LOW1','LOW2','LOW3','LOW4','LOW5','LOW6']].max(axis=1)
data['LOW_CHG'] = np.log(data['minLOW']/data.CLOSE.shift(1))*100

data = data[data.HIGH_CHG.notnull() & data.CLOSE_CHG_7.notnull()].reset_index(drop=True)
all_factorlist = "atr,bias,cci,dma,dmi,dpo,macd,mtm,priceosc,roc,rsi,sar,si"
factorlist = all_factorlist.upper().replace(' ', '').split(",")
datelist = data['date']
# 定义常量
days = 50
time_step = 1

interstra = Intervalstrategy(7)
pnl = pd.DataFrame(datelist)
pnl['y'] = 0.0
pnl['yhat_lstm'] = 0.0
valid_num = 10

for j, date in enumerate(datelist):
    print(date)
    if j < days+valid_num:
        continue
    # 滚动样本
    X = data.loc[j - days - valid_num: j, factorlist]
    # y_raw = data.loc[j - days + 1: j, 'PCT_CHG']
    y_raw = data.loc[j - days - valid_num: j, 'CLOSE_CHG_1']
    # 延长样本
    # X = model.loc[:j-1, 'ADTM':'SI']
    # y_raw = model.loc[1:j-1, 'PCT_CHG']
    scaler = preprocessing.StandardScaler().fit(X)
    X = scaler.transform(X)
    quantile_30 = y_raw.quantile(0.3)
    quantile_70 = y_raw.quantile(0.7)


    def _get_label(x):
        if x >= 0:
            return 1
        else:
            return 0


    y = y_raw.apply(lambda x: _get_label(x)).values

    # 主成分分析
    pca = PCA(n_components=7)
    pca.fit(X)
    X = pca.fit_transform(X)

    # 转变数据类型
    train_x, train_y, valid_x, valid_y = interstra.transform_data(X, y, time_step, valid_num)

    # 模型训练和预测
    # train_lstm(train_x,train_y,time_step)
    if (j-(days+valid_num)) % valid_num == 0:  # 受限于计算速度，这里每20天更新下模型
        interstra.train_lstm(train_x, train_y, valid_x, valid_y)
    predict2 = interstra.prediction(valid_x[:1, :])

    ## 结果输出
    pnl.loc[j-valid_num, 'y'] = data.loc[j-valid_num, 'CLOSE_CHG_1']
    pnl.loc[j-valid_num, 'yhat_lstm'] = np.argmax(predict2[0])-1
    pnl.loc[j-valid_num, 'yhat_lstm_0'] = predict2[0, 0]
    pnl.loc[j-valid_num, 'yhat_lstm_1'] = predict2[0, 1]
    # print(date, metrics.accuracy_score(y[time_step - 1:], sample_yhat - 1), predict2)

# pnl = pnl.loc[days + 1:, ]
pnl.set_index(["date"], inplace=True)
pnl.to_excel("pnl_CLOSE_CHG_1.csv")
interstra.savemodel("./model_dropout_CLOSE_CHG_1.h5")
print('Done!')

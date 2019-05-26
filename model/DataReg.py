
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


# 验证数据集中的异常值
def is_outlier(data_sets,n=3):
    res = np.zeros(len(data_sets))
    if all(np.isnan(data_sets)) == True:
        return res
    data_std = np.std(data_sets[np.isnan(data_sets)==False])
    data_mean = np.mean(data_sets[np.isnan(data_sets)==False])
    for i, data in enumerate(data_sets):
        if (data >= data_mean - n * data_std) and (data <= data_mean + n * data_std):
            res[i] = False
        else:
            res[i] = True  # 是异常值
    return res


def keras_model(X,Y,Dense_layer,input_shape,n_classes=2,):
    from keras.models import Sequential
    from keras.layers import Dense, Activation
    # from keras.optimizers import SGD
    model = Sequential()
    model.add(Dense(units=64, input_shape=input_shape,activation="relu"))
    # model.add(Activation("relu"))
    model.add(Dense(units=n_classes, activation="softmax"))
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    # model.compile(loss='categorical_crossentropy', optimizer=SGD(lr=0.01, momentum=0.9, nesterov=True))
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=0)
    model.fit(x_train, y_train, epochs=5, batch_size=32)
    # model.train_on_batch(x_train, y_test)
    score = model.evaluate(x_test, y_test, batch_size=128)
    # classes = model.predict(x_test, batch_size=128)
    return model, score


# 数据分为哪个等级
def y_reg(x,series):
    i = 0
    for hist_plot in series:
        if x <= hist_plot:
            return i
        else:
            i += 1
    return i

def qb_reg(df): # params: df数据框
    bid_diff = df['bid'].dropna().diff()
    # plt.hist(bid_diff)
    df['createDateTime']

# 绘制ROC图形
def plotROC(x, y, tr=0.5, fr=0.5, isplot=True):
    y1_num = sum(y == 1)
    y0_num = sum(y == 0)
    tpr_list = []
    fpr_list = []
    for i in np.arange(0, 100, 1):
        x0 = np.percentile(x, i)
        tpr_list.append(sum(y[x > x0] == 1) / y1_num)
        fpr_list.append(sum(y[x > x0] == 0) / y0_num)
    index = np.argmax(list(map(lambda _x, _y: tr*_x-fr*_y, tpr_list, fpr_list)))
    auc = sum((np.array(tpr_list)-np.array(fpr_list))[1:]*(np.array(fpr_list)[1:]-np.array(fpr_list[:-1])))
    if isplot:
        plt.figure(figsize=(7, 6))
        plt.xlabel('FPR value')
        plt.ylabel('TPR value')
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.plot(fpr_list, tpr_list)
        plt.plot([0, 1], [0, 1], 'r--')
        plt.plot([fpr_list[index], fpr_list[index]], [fpr_list[index], tpr_list[index]])
        plt.title("ROC curve")
        plt.savefig("fpr-tpr.jpg")
        plt.show()
    return np.percentile(x, index), tpr_list[index]-fpr_list[index], auc

def classificationbyval(x, y):
    ks_array = np.zeros(100)
    auc_array = np.zeros(100)
    y0_array = np.zeros(100)
    x0_array = np.zeros(100)
    for i in np.arange(0, 100, 1):
        y0_array[i] = np.percentile(y, i)
        x0_array[i], ks_array[i], auc_array[i] = plotROC(x,y>y0_array[i],isplot=False)
    index = auc_array.argmax()
    plotROC(x,y>y0_array[index])
    return x0_array[index], y0_array[index], max(auc_array)









import numpy as np
# import tensorflow as tf
import keras
from keras.callbacks import TensorBoard


class Intervalstrategy:
    rnn_unit = 50  # hidden layer units
    input_size = 7
    output_size = 3
    lr = 0.0006

    def __init__(self, input_d):
        self.model = keras.Sequential([
            # keras.layers.LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])),
            keras.layers.Dense(10, activation='relu', input_shape=(input_d,)),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(10, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(3, activation='softmax')
        ])
        self.model.compile(optimizer='rmsprop',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

    # 转变数据格式
    def transform_data(self, raw_X, raw_Y, time_step=1, valid_num=5):
        # 转变数据类型
        tx = []
        for i in range(time_step-1, len(raw_X)):
            tx.append(raw_X[i - time_step + 1:i + 1].reshape(-1))
        tx = np.array(tx, dtype=np.float32)
        train_x = tx[:-valid_num, :]
        # train_x = train_x.reshape(days-time_step+2,5,7)
        valid_x = tx[-valid_num:, :]
        # test_x = test_x.reshape(1, time_step, input_size)

        ty = []
        for i in range(time_step - 1 , len(raw_Y)):
            if raw_Y[i] == 0:
                ty.append([1, 0, 0])
            elif raw_Y[i] == 1:
                ty.append([0, 1, 0])
            else:
                ty.append([0, 0, 1])

        ty = np.array(ty, dtype=np.float32)
        train_y = ty[:-valid_num]
        valid_y = ty[-valid_num:]
        # train_y = train_y.reshape(len(y[time_step - 1:]), output_size)
        return train_x, train_y, valid_x, valid_y

    # ——————————————————训练模型——————————————————
    def train_lstm(self, train_x, train_y, valid_x, valid_y, logdir, epochs=100):
        self.model.fit(train_x, train_y, batch_size=32, epochs=epochs,
                       validation_data=(valid_x, valid_y),
                       callbacks=[TensorBoard(log_dir=logdir, write_images=1, histogram_freq=1)])

        # Save entire model to a HDF5 file
        # self.model.save('my_model.h5')

    def prediction(self, x, time_step=5):
        # self.model = keras.models.load_model('my_model.h5')
        sample_yhat = self.model.predict(x, batch_size=32)
        return sample_yhat

    def evaluate(self, train_x, train_y):
        self.model.evaluate(train_x, train_y, batch_size=32)

    def loadmodel(self,modelpath):
        self.model = keras.models.load_model(modelpath)

    def savemodel(self,modelpath):
        self.model.save(modelpath)


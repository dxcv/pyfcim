import time
import talib
import pandas as pd
from WindPy import *
from scripts.AutoModel import *
from copy import deepcopy
import pickle


class TradeSignal:
    TimeSeries = []  # 生成时间序列，规整化
    Seq = []  # 规整化后的时间序列
    CurrentSeqTime = 0  # 当前规整时间序列的最后一个时间节点
    OrderList = []
    KAMASeries = []
    dt = 0
    dateRange = []
    index = 0
    PositionList = []
    high = 0  # 记录当前最高值
    # PositionID = 0

    def __init__(self):
        self.TempInData = InData()

    def dayInit(self):
        self.dt = datetime.now()
        self.dateRange = pd.date_range(start="%s 9:30:00" % self.dt.strftime("%Y-%m-%d"), end="%s 11:30:00" % self.dt.strftime("%Y-%m-%d"), freq="min").append(
            pd.date_range(start="%s 13:00:00" % self.dt.strftime("%Y-%m-%d"), end="%s 15:00:00" % self.dt.strftime("%Y-%m-%d"), freq="min"))
        self.index = 0
        # with open('datafile.pk', 'rb') as f:
        #     self.Seq = pickle.load(f)

    def dayOver(self):
        with open('datafile.pk', 'wb') as f:
            pickle.dump(self.Seq[-100, :], f)

    # 将新进的tick数据加进时间序列中
    def addSeq(self, _indata):
        print(_indata.Times)
        print(_indata.price)
        self.TimeSeries.append([_indata.Times, _indata.price])
        if self.index < len(self.dateRange)-1 and (_indata.Times > self.dateRange[self.index]):
            if _indata.Times < self.dateRange[self.index]:
                self.TempInData = _indata
            elif _indata.Times > self.dateRange[self.index]:
                tempSeries = self.dateRange[(self.dateRange < _indata.Times)][self.index:]
                self.index += len(tempSeries)
                for _i in np.arange(len(tempSeries)):
                    print([tempSeries[_i], self.TempInData.price])
                    self.Seq.append([tempSeries[_i], self.TempInData.price])
                self.TempInData = _indata
                self.KAMA()
            elif _indata.Times == self.dateRange[self.index]:
                self.index += 1
                self.Seq.append([self.dateRange[self.index], _indata.price])
                self.TempInData = _indata
                self.KAMA()
        self.alert1(_indata)

    def KAMA(self):  # 计算均线
        try:
            if self.Seq.__len__() >= 30:
                temp = talib.KAMA(np.array(self.Seq)[-30:, 1].reshape(-1).astype(float), 20)[-1]
                if ~np.isnan(temp):
                    self.KAMASeries.append(temp)
            else:
                print('Seq序列不足')
        except Exception as e:
            print(e)

    def alert(self, _indata):  # bolling线策略
        if self.KAMASeries.__len__() > 60:
            print("KAMA:%f" % self.KAMASeries[-1])
            if _indata.price < self.KAMASeries[-1] - 0.005:
                print("%(Times)s  %(Codes)s: %(price)s 买入" % {'Times': _indata.Times, 'Codes': _indata.Codes, 'price': _indata.price})
                self.insertToDB(_indata, '买入')

            elif _indata.price > self.KAMASeries[-1] + 0.01:
                print("%(Times)s  %(Codes)s: %(price)s 卖出" % {'Times': _indata.Times, 'Codes': _indata.Codes,
                                                              'price': _indata.price})
                self.insertToDB(_indata, '卖出')

    # 根据订单生存时间，将超过时间的订单撤销
    def cancelOrder(self, dt: datetime, exist_sec=60):
        db = Session()
        try:
            for order in self.OrderList:
                if dt - order.dt > timedelta(seconds=exist_sec):
                    order.cancel = 1
                    db.add(deepcopy(order))
                    self.OrderList.remove(order)
        except Exception as e:
            print(e)
        finally:
            db.commit()
            db.close()

    def positionDetail(self):
        db = Session()
        self.PositionList = db.query(Position).all()

    def alert1(self, _indata):  # 冲击均线策略
        db = Session()
        try:
            temp = list(np.array(self.Seq)[-30:, 1])
            temp.append(_indata.price)
            current_KAMA = talib.KAMA(np.array(temp).astype(float), 20)[-1]

            if np.all([_indata.price - self.KAMASeries[-1] < -0.2, _indata.price >= current_KAMA - 0.1,
                       _indata.price < current_KAMA - 0.06]):
                temp_buy_order = Order(_indata.Times, 1, _indata.Codes, _indata.price + 0.01, 1)
                if temp_buy_order not in self.OrderList and self.PositionList.__len__() <= 10:
                    print(temp_buy_order)
                    db.add(temp_buy_order)
                    self.OrderList.append(deepcopy(temp_buy_order))
                temp_sell_order = Order(_indata.Times, 0, _indata.Codes, _indata.price + 0.02, 1)
                if temp_sell_order not in self.OrderList:
                    print(temp_sell_order)
                    db.add(temp_sell_order)
                    self.OrderList.append(deepcopy(temp_sell_order))

            temp_buy_order = Order(_indata.Times, 1, _indata.Codes, round(self.KAMASeries[-1] - 0.28, 3), 2)
            if temp_buy_order not in self.OrderList and self.PositionList.__len__() <= 10:
                print(temp_buy_order)
                db.add(temp_buy_order)
                self.OrderList.append(deepcopy(temp_buy_order))

        except Exception as e:
            print(e)
        finally:
            db.commit()
            db.close()

    def tradeSignalCallback(self, indatas):
        if 'RT_LAST' in indatas.Fields:
            indata = InData()
            indata.Times = pd.to_datetime(indatas.Times[0])
            indata.Codes = indatas.Codes[0]
            dicts = {}
            for field, data in zip(indatas.Fields, indatas.Data):
                dicts[field] = data[0]
            indata.price = dicts['RT_LAST'] if 'RT_LAST' in dicts.keys() else None
            indata.ask1 = dicts['RT_ASK1'] if 'RT_ASK1' in dicts.keys() else None
            indata.bid1 = dicts['RT_BID1'] if 'RT_BID1' in dicts.keys() else None
            self.addSeq(indata)

    def start(self, code):
        w.start()
        w.wsq(code, "rt_date,rt_time,rt_pre_close,rt_open,rt_high,rt_low,rt_last,rt_last_amt,rt_last_vol,rt_ask1,rt_bid1", func=self.tradeSignalCallback)
        while 1:
            self.positionDetail()
            time.sleep(30)


class InData:
    def __init__(self):
        self.Times = ""
        self.Codes = ""
        self.price = 0
        self.ask1 = 0
        self.bid1 = 0


if __name__ == '__main__':
    tradeSignal = TradeSignal()
    tradeSignal.dayInit()
    #
    # tradeSignal.start('113026.SH')

    df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\113011光大转债tick数据.xlsx")
    for i in range(df.shape[0]):
        indata = InData()
        indata.Times = pd.to_datetime("20190527 %s" % df.time[i].strftime("%H:%M:%S"))
        indata.Codes = "113011.SH"
        indata.price = df.price[i]
        tradeSignal.addSeq(indata)

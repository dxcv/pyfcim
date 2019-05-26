import numpy as np
from datetime import datetime, timedelta
import talib
import time
import pandas as pd
from WindPy import *
import pymssql

###
# 用于计算某只券的报买报卖时间节点
###
class TradeSignal:
    TimeSeries = [] # 生成时间序列，规整化
    Seq = [] # 规整化后的时间序列
    CurrentSeqTime = 0 # 当前规整时间序列的最后一个时间节点

    KAMASeries = []
    dt = 0
    dateRange = []
    index = 0
    PositionPriceList = []
    high = 0 # 记录当前最高值

    def __init__(self):
        self.TempInData = InData()

    def dayInit(self):
        self.dt = datetime.now()
        self.dateRange = pd.date_range(start="%s 9:30:00" % self.dt.strftime("%Y-%m-%d"), end="%s 11:30:00" % self.dt.strftime("%Y-%m-%d"), freq="min").append(
            pd.date_range(start="%s 13:00:00" % self.dt.strftime("%Y-%m-%d"), end="%s 15:00:00" % self.dt.strftime("%Y-%m-%d"), freq="min"))
        self.index = 0

    def addSeq(self, indata):
        print(indata.Times)
        print(indata.price)
        self.TimeSeries.append([indata.Times,indata.price])
        if self.index < len(self.dateRange)-1 and (indata.Times > self.dateRange[self.index]):
            if indata.Times < self.dateRange[self.index+1]:
                self.TempInData = indata
            elif indata.Times > self.dateRange[self.index+1]:
                tempSeries = self.dateRange[(self.dateRange < indata.Times)][self.index:]
                # print(self.index)
                self.index += len(tempSeries)
                for i in np.arange(len(tempSeries[:-1])):
                    print([tempSeries[i],self.TempInData.price])
                    self.Seq.append([tempSeries[i],self.TempInData.price])
                self.TempInData = indata
                self.KAMA()
            elif indata.Times == self.dateRange[self.index+1]:
                self.index += 1
                self.Seq.append([self.dateRange[self.index], indata.price])
                self.Seq.append([self.dateRange[self.index+1], indata.price])
                self.TempInData = indata
                self.KAMA()
        self.alert1(indata)

    def KAMA(self): # 计算均线
        try:
            temp = talib.KAMA(np.array(self.Seq)[-40:, 1].reshape(-1).astype(float), 20)[-1]
            if ~np.isnan(temp):
                self.KAMASeries.append(temp)
        except:
            print("数据不足")

    def alert(self, indata): # bolling线策略
        if self.KAMASeries.__len__() > 60:
            print("KAMA:%f" % self.KAMASeries[-1])
            if indata.price < self.KAMASeries[-1] - 0.005:
                print("%(Times)s  %(Codes)s: %(price)s 买入" %{'Times':indata.Times,'Codes':indata.Codes,'price':indata.price})
                self.insertToDB(indata, '买入')

            elif indata.price > self.KAMASeries[-1] + 0.01:
                print("%(Times)s  %(Codes)s: %(price)s 卖出" % {'Times': indata.Times, 'Codes': indata.Codes,
                                                              'price': indata.price})
                self.insertToDB(indata, '卖出')

    def alert1(self,indata): # 冲击均线策略
        try:
            temp = list(np.array(self.Seq)[-30:,1])
            temp.append(indata.price)
            current_KAMA = talib.KAMA(np.array(temp).astype(float), 20)[-1]
            if self.PositionPriceList.__len__() > 0:
                if self.high - indata.price >= 0.05:
                    print("%(Times)s  %(Codes)s: %(price)s 卖出" % {'Times': indata.Times, 'Codes': indata.Codes,
                                                                  'price': indata.price})
                    print("%(Times)s  %(Codes)s: %(price)s 卖出" % {'Times': indata.Times, 'Codes': indata.Codes,
                                                                  'price': indata.price})
                    self.PositionPriceList = []
                    self.high = 0

            if self.PositionPriceList.__len__() == 0:
                if indata.price >= self.TimeSeries[-1][1] and self.Seq[-1][1] - self.KAMASeries[-1]<-0.12 and indata.price >= current_KAMA - 1 and indata.price < current_KAMA-0.06:
                #if indata.price >= self.TimeSeries[-1][1] and self.Seq[-1][1] - self.KAMASeries[-1] < -0.06 and indata.price < current_KAMA - 0.04:

                    print("%(Times)s  %(Codes)s: %(price)s 买入" % {'Times': indata.Times, 'Codes': indata.Codes,
                                                                  'price': indata.price + 0.01})
                    print("%(Times)s  %(Codes)s: %(price)s 卖出" % {'Times': indata.Times, 'Codes': indata.Codes,
                                                                  'price': indata.price + 0.02})

                    self.PositionPriceList.append(indata.price)

                print("%(Times)s  %(Codes)s: %(price)s 买入" % {'Times': indata.Times, 'Codes': indata.Codes,
                                                              'price': self.KAMASeries[-1]-0.28})
                print("%(Times)s  %(Codes)s: %(price)s 卖出" % {'Times': indata.Times, 'Codes': indata.Codes,
                                                              'price': self.KAMASeries[-1] - 0.1})
        except Exception as e:
            print(e)


    def tradeSignalCallback(self,indatas):
        if 'RT_LAST' in indatas.Fields:
            indata = InData()
            indata.Times = pd.to_datetime(indatas.Times[0])
            indata.Codes = indatas.Codes[0]
            indata.price = float(indatas.Data[indatas.Fields.index('RT_LAST')][0])

            self.addSeq(indata)
        #print(indatas)
        #print(self.index)
        #print(self.Seq[-1])
        print("-----------")

    def insertToDB(self,indata,direction):
        try:
            conn_43 = pymssql.connect(host="10.28.7.43", user="bond", password='bond', database="InvestSystem")
            cur = conn_43.cursor()
            sql = """insert into TradeSignal (dt,code,price,direction) values ('%(Times)s','%(Codes)s',%(price)f,'%(direction)s')""" % {'Times': indata.Times.strftime("%Y-%m-%d %H:%M:%S"), 'Codes': indata.Codes,
                                                                  'price': indata.price,'direction':direction}
            cur.execute(sql)
            conn_43.commit()
            return 1
        except Exception as e:
            print(e)
            return 0

    def start(self, code):
        w.start()
        w.wsq(code, "rt_date,rt_time,rt_pre_close,rt_open,rt_high,rt_low,rt_last,rt_last_amt,rt_last_vol,rt_ask1,rt_bid1", func=self.tradeSignalCallback)

class InData:
    def __init__(self):
        self.Times = ""
        self.Codes = ""
        self.price = 0


if __name__ == '__main__':
    tradeSignal = TradeSignal()
    tradeSignal.dayInit()
    #
    # tradeSignal.start('113026.SH')

    df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\113011光大转债tick数据.xlsx")
    for i in range(df.shape[0]):
        indata = InData()
        indata.Times = pd.to_datetime("20190524 %s"%df.time[i].strftime("%H:%M:%S"))
        indata.Codes = "113011.SH"
        indata.price = df.price[i]
        tradeSignal.addSeq(indata)

    #
    # tradeSignal1 = TradeSignal()
    # tradeSignal1.dayInit()
    # tradeSignal1.start('127010.SZ')

    # indata = InData()
    # indata.Times = pd.to_datetime("20190522 10:31:10.432")
    # indata.Codes = "000001.SZ"
    # indata.price = 0
    # tradeSignal.addSeq(indata)
    # indata = InData()
    # indata.Times = pd.to_datetime("20190522 10:32:10.432")
    # indata.Codes = "000001.SZ"
    # indata.price = -2
    # tradeSignal.addSeq(indata)
    # indata = InData()
    # indata.Times = pd.to_datetime("20190522 10:34:43.432")
    # indata.Codes = "000001.SZ"
    # indata.price = -2
    # tradeSignal.addSeq(indata)
    #
    # indata = InData()
    # indata.Times = pd.to_datetime("20190522 09:32:20.432")
    # indata.Codes = "000001.SZ"
    # indata.price = 12.54
    # tradeSignal.addSeq(indata)

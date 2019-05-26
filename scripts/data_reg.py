# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 20:19:26 2018

@author: l_cry
"""
import pandas as pd
import pymssql
from sqlalchemy import create_engine
import datetime
import numpy as np
#数据获取连接
conn = pymssql.connect(host = "192.168.87.57",user = "saread",password = 'sa',database = "VirtualExchange")

#数据存储连接
engine = create_engine('mssql+pyodbc://sa:sa123@localhost:1433/data_reg?driver=SQL+Server')


# 获取制定时间范围内的数据
def data_fetch(start_time,end_time):
    fetch_data_sql = """SELECT
                *
                FROM
                dbo.FutureHQ
                WHERE
                dbo.FutureHQ.SCode LIKE 'T%%' AND
                dbo.FutureHQ.updatetime >= '%s' AND
                dbo.FutureHQ.updatetime < '%s'""" % (start_time, end_time)
    df = pd.read_sql(sql=fetch_data_sql, con=conn)
    return df

def data_fetch_code(scode, start_time, end_time):
    fetch_data_sql = """SELECT
                SCode,updatetime
                FROM
                dbo.FutureHQ_reg
                WHERE
                dbo.FutureHQ_reg.SCode=%s AND
                dbo.FutureHQ_reg.updatetime >= '%s' AND
                dbo.FutureHQ_reg.updatetime < '%s'""" % (scode,start_time, end_time)
    df = pd.read_sql(sql=fetch_data_sql, con=engine)
    return df
    
    
# 将不同代码的数据分离，对同种数据进行聚合处理
def data_divide(df):return df.groupby('SCode').apply(data_resample)

     
     

# 按秒级别对数据进行重采样
def data_resample(df1):
    TradeVolume = df1.TradeVolume.resample('1s').last().fillna(method='ffill').rename('TradeVolume',inplace=True)
    Position = df1.TradeValue.resample('1s').last().fillna(method='ffill').rename('Position',inplace=True)
    NewPrice = df1.NewPrice.resample('1s').last().fillna(method='ffill').rename('NewPrice',inplace=True)
    BuyPrice1 = df1.BuyPrice1.resample('1s').last().fillna(method='ffill').rename('BuyPrice1',inplace=True)
    BuyVol1 = df1.BuyVol1.resample('1s').last().fillna(method='ffill').rename('BuyVol1',inplace=True)
    SellPrice1 = df1.SelPrice1.resample('1s').last().fillna(method='ffill').rename('SellPrice1',inplace=True)
    SellVol1 = df1.SelVol1.resample('1s').last().fillna(method='ffill').rename('SellVol1',inplace=True)  
    PrePrice = df1.PrePrice.resample('1s').last().fillna(method='ffill').rename('PrePrice',inplace=True)
    OpenPrice = df1.OpenPrice.resample('1s').last().fillna(method='ffill').rename('OpenPrice',inplace=True)
    HighPrice = df1.HighPrice.resample('1s').last().fillna(method='ffill').rename('HighPrice',inplace=True)
    LowPrice = df1.LowPrice.resample('1s').last().fillna(method='ffill').rename('LowPrice',inplace=True)
    df2 = pd.concat([TradeVolume, Position, NewPrice, BuyPrice1, BuyVol1, SellPrice1, SellVol1, PrePrice, OpenPrice, HighPrice, LowPrice], axis=1)
    #######################################################
    # 对其到数据框
    #######################################################
    Datestr = df2.index[0].strftime("%Y-%m-%d") 
    if df1.index[0].time().hour<12:
        DateIndex = pd.date_range(start=Datestr+" 09:15:01",end=Datestr+" 11:30:00",freq='s')
    else:
        DateIndex = pd.date_range(start=Datestr+" 13:00:01",end=Datestr+" 15:16:00",freq='s')
    #DateIndex = pd.DatetimeIndex(np.append(DateIndex1.values,DateIndex2.values))
    df2 = df2.reindex(DateIndex)
    #df2['SCode'] = df2.SCode.fillna(method='ffill').fillna(method='bfill')
    df2['TradeVolume'] = df2.TradeVolume.fillna(method='ffill').fillna(0)
    #df2['Position'] = df2.Position.fillna(method='ffill').fillna(method='bfill')
    df2[['Position', 'NewPrice', 'BuyPrice1', 'BuyVol1',
       'SellPrice1', 'SellVol1', 'PrePrice', 'OpenPrice', 'HighPrice',
       'LowPrice']] = df2[['Position', 'NewPrice', 'BuyPrice1', 'BuyVol1',
       'SellPrice1', 'SellVol1', 'PrePrice', 'OpenPrice', 'HighPrice',
       'LowPrice']].fillna(method='ffill').fillna(method='bfill')
    return df2



#######################################
#初始入库脚本
#######################################
#date_range = pd.date_range(start='2018-11-11 00:00:00',end='2018-11-14 00:00:00',freq='d')
#for start_time,end_time in zip(date_range[:-1],date_range[1:]):
#    df = data_fetch(start_time, end_time)
#    dfam = df[(df.updatetime.apply(lambda x: x.time())<datetime.time(11,31)) & (df.updatetime.apply(lambda x: x.time())>=datetime.time(9,15))].copy()
#    dfpm = df[(df.updatetime.apply(lambda x: x.time())<datetime.time(15,16)) & (df.updatetime.apply(lambda x: x.time())>=datetime.time(13,0))].copy()
#    dfam.index =dfam.updatetime
#    dfpm.index =dfpm.updatetime
#    df2 = pd.concat([data_divide(dfam),data_divide(dfpm)]).reset_index()
#    if "level_1" in df2.columns:
#        df2.rename(columns={"level_1":'updatetime'},inplace=True)    
#    df2.to_sql(name="FutureHQ_reg",con=engine,index=False,if_exists='append',chunksize=40000)
#    print("================================\n%s日数据已处理\n"% start_time)


    
########################################
#   日常任务
########################################
now = datetime.datetime.now()
yesterday = now - datetime.timedelta(1)
tomorrow = now + datetime.timedelta(1)
df  = data_fetch(yesterday.strftime("%Y-%m-%d 00:00:00"),now.strftime("%Y-%m-%d 00:00:00"))
#df  = data_fetch('2018-04-03','2018-04-04')
#df  = data_fetch('2018-11-01','2018-11-02')
dfam = df[(df.updatetime.apply(lambda x: x.time())<datetime.time(11,31)) & (df.updatetime.apply(lambda x: x.time())>=datetime.time(9,15))].copy()
dfpm = df[(df.updatetime.apply(lambda x: x.time())<datetime.time(15,16)) & (df.updatetime.apply(lambda x: x.time())>=datetime.time(13,0))].copy()
dfam.index = dfam.updatetime
dfpm.index = dfpm.updatetime
df2 = pd.concat([data_divide(dfam),data_divide(dfpm)]).reset_index()
if "level_1" in df2.columns:
    df2.rename(columns={"level_1":'updatetime'},inplace=True)
df2.to_sql(name="FutureHQ_reg",con=engine,index=False,if_exists='append',chunksize=4000)
print("================================\n%s日数据已处理\n Have a nice day\n"% yesterday.strftime("%Y-%m-%d"))
 

#########################################
#####TEST代码
#########################################
#df = data_fetch('2018-06-04 00:00:00','2018-06-05 00:00:00')[['BuyPrice1','BuyVol1','NewPrice','SCode','TradeVolume',  'updatetime']]
#dfam = df[(df.updatetime.apply(lambda x: x.time())<datetime.time(11,31)) & (df.updatetime.apply(lambda x: x.time())>=datetime.time(9,15))].copy()
#dfpm = df[(df.updatetime.apply(lambda x: x.time())<datetime.time(15,16)) & (df.updatetime.apply(lambda x: x.time())>=datetime.time(13,0))].copy()
#
#dfam.index = dfam.updatetime
#dfpm.index = dfpm.updatetime
#data_divide(dfpm)
#
#df2 = pd.concat([data_divide(dfam),data_divide(dfpm)])









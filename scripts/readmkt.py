import numpy as np
import pymssql
from sqlalchemy import create_engine
import time
from datetime import datetime, timedelta
# engine_103 = create_engine('mssql+pyodbc://sa:tcl+nftx@10.28.7.43:1433/VirtualExchange?driver=SQL+Server')
conn_43 = pymssql.connect(host = "10.28.7.43",user = "sa",password = 'tcl+nftx',database = "VirtualExchange")
MD001header = ["MDStreamID","SecurityID","Symbol","TradeVolume","TotalValueTraded","PreClosePx","OpenPrice","HighPrice","LowPrice","TradePrice","ClosePx","TradingPhaseCode","Timestamp"]
MD002and03header = ["MDStreamID","SecurityID","Symbol","TradeVolume","TotalValueTraded","PreClosePx","OpenPrice","HighPrice","LowPrice","TradePrice","ClosePx","BuyPrice1","BuyVolume1",
              "SellPrice1","SellVolume1","BuyPrice2","BuyVolume2","SellPrice2","SellVolume2","BuyPrice3","BuyVolume3","SellPrice3","SellVolume3","BuyPrice4","BuyVolume4","SellPrice4",
              "SellVolume4","BuyPrice5","BuyVolume5","SellPrice5","SellVolume5","TradingPhaseCode","Timestamp"]
MD004header = ["MDStreamID","SecurityID","Symbol","TradeVolume","TotalValueTraded","PreClosePx","OpenPrice","HighPrice","LowPrice","TradePrice","ClosePx","BuyPrice1","BuyVolume1",
              "SellPrice1","SellVolume1","BuyPrice2","BuyVolume2","SellPrice2","SellVolume2","BuyPrice3","BuyVolume3","SellPrice3","SellVolume3","BuyPrice4","BuyVolume4","SellPrice4",
              "SellVolume4","BuyPrice5","BuyVolume5","SellPrice5","SellVolume5","PreCloseIOPV","IOPV","TradingPhaseCode","Timestamp"]




def str2float(s):
    try:
        return float(s)
    except:
        return np.nan


def insertIntoDB(data):
    cursor = conn_43.cursor()
    columns_list = []
    values_list = []
    for item in data.keys():
        columns_list.append(item)
        if item != "Timestamp":
            if type(data[item]) is str:
                temp = '\'' + str(data[item]) + '\''
            else:
                if type(data[item]) in [int, float] and np.isnan(data[item]):
                    temp = 'null'
                else:
                    temp = str(data[item])
        else:
            temp = '\'' + datetime.now().strftime("%H:%M:%S.%f")[:-3] + '\''
        values_list.append(temp)
    # sql = """
    # INSERT INTO MKTDT00 (%s) VALUES (%s)
    # """% (','.join(columns_list), ','.join(values_list))
    set_list = []
    for col, val in zip(columns_list, values_list):
        set_list.append(col + "=" + val)

    sql = """
    update MKTDT00 SET %s WHERE SecurityID=%s
    """ % (','.join(set_list), '\'' + data['SecurityID'] + '\'')

    cursor.execute(sql)
    conn_43.commit()

def fread():
    dataset = {}
    codeList = []
    with open("C:\\Users\\l_cry\\Desktop\\data\\MKTDT00.TXT") as fp:
        codeList = fp.read().replace(" ","").split("\n")

    if codeList.__len__() > 0:
        for line in codeList:
            row = line.split("|")
            data = dict()

            if row[0] == 'MD001':
                header = MD001header
            elif row[0] == "MD002" or row[0] == "MD003":
                header = MD002and03header
            elif row[0] == "MD004":
                header = MD004header
            else:
                continue
            for key,val in zip(header, row):
                if key in ("TradeVolume", "TotalValueTraded", "PreClosePx", "OpenPrice","HighPrice","LowPrice","TradePrice","ClosePx","BuyPrice1","BuyVolume1","SellPrice1","SellVolume1","BuyPrice2","BuyVolume2","SellPrice2","SellVolume2","BuyPrice3","BuyVolume3","SellPrice3","SellVolume3","BuyPrice4","BuyVolume4","SellPrice4","SellVolume4","BuyPrice5","BuyVolume5","SellPrice5","SellVolume5","PreCloseIOPV","IOPV"):
                    data[key] = str2float(val)
                else:
                    data[key] = val
            dataset[row[1]] = data
    return dataset


def compare(datadict,newdict):
    insertdict = dict()
    for item in newdict.keys():
        if item in datadict.keys():
            for key in newdict[item]:
                if newdict[item][key] != datadict[item][key]:
                    datadict[item] = newdict[item]
                    insertdict[item] = newdict[item]
                    break

        else:
            datadict[item] = newdict[item]
            insertdict[item] = newdict[item]
    return insertdict

datadict={}

while datetime.now().hour < 16:
    dataset = fread()
    insertdict = compare(datadict, dataset)
    print('fresh' + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    for key in insertdict.keys():
        if insertdict[key]['MDStreamID'] == "MD003" and (
                insertdict[key]['SecurityID'] in ("018009", "113013", "019009")):
            insertIntoDB(insertdict[key])
            print((insertdict[key]['Symbol'], insertdict[key]['SecurityID'], insertdict[key]['TradePrice']))
        elif insertdict[key]['MDStreamID'] == "MD004" and insertdict[key]['SecurityID'] in (
        "511010", "511020", "511030"):
            insertIntoDB(insertdict[key])
            print((insertdict[key]['Symbol'], insertdict[key]['SecurityID'], insertdict[key]['TradePrice']))

print("over")













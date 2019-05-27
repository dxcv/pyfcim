import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from WindPy import *


engine = create_engine('mssql+pyodbc://bond:bond@10.28.7.43/InvestSystem?driver=SQL+Server')

# df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\相对价值计算.xlsx",index_col="日期")
# df = df.replace(0,np.nan).fillna(method='ffill')

def g(arr, startDateIndex):
    StartIndex = max(startDateIndex, np.isnan(arr).sum())
    return list(map(lambda i : (arr[0,i] > arr[0, baseDateIndex:i]).sum()/(~np.isnan(arr[0, baseDateIndex:i])).sum() if i >= StartIndex else np.nan, np.arange(0, rows)))

def g1(arr,startDateIndex):
    return [(arr[0, rows-1] > arr[0, baseDateIndex:(rows-1)]).sum()/(~np.isnan(arr[0, baseDateIndex:(rows-1)])).sum()]

# @jit(nogil=True)
def ComparedPriceCal1(X, f):
    NanNumArr = np.isnan(X).sum(0)
    XMat = np.matrix(X)
    def h(XMatArr):
        XMat0 = np.apply_along_axis(f, 0, XMatArr.reshape((-1, 1)) - XMat, startDateIndex)
        return (XMat0.sum(1) / (cols - 1))
    XMatNotes = np.apply_along_axis(h, 0, XMat)

    return XMatNotes


if __name__ == '__main__':
    w.start()
    columns = ['中债国债到期收益率:1年', '中债国债到期收益率:3年', '中债国债到期收益率:5年', '中债国债到期收益率:7年',
       '中债国债到期收益率:10年', '中债地方政府债到期收益率(AAA):1年', '中债地方政府债到期收益率(AAA):3年',
       '中债地方政府债到期收益率(AAA):5年', '中债地方政府债到期收益率(AAA):7年', '中债地方政府债到期收益率(AAA):10年',
       '中债国开债到期收益率:1年', '中债国开债到期收益率:3年', '中债国开债到期收益率:5年', '中债国开债到期收益率:7年',
       '中债国开债到期收益率:10年', '中债进出口行债到期收益率:1年', '中债进出口行债到期收益率:3年',
       '中债进出口行债到期收益率:5年', '中债进出口行债到期收益率:7年', '中债进出口行债到期收益率:10年',
       '中债农发行债到期收益率:1年', '中债农发行债到期收益率:3年', '中债农发行债到期收益率:5年', '中债农发行债到期收益率:7年',
       '中债农发行债到期收益率:10年', '中债中短期票据到期收益率(AAA):1年', '中债中短期票据到期收益率(AAA):3年',
       '中债中短期票据到期收益率(AAA):5年', '中债中短期票据到期收益率(AAA):7年', '中债中短期票据到期收益率(AAA):10年',
       '中债中短期票据到期收益率(AA+):1年', '中债中短期票据到期收益率(AA+):3年', '中债中短期票据到期收益率(AA+):5年',
       '中债中短期票据到期收益率(AA+):7年', '中债中短期票据到期收益率(AA+):10年', '中债中短期票据到期收益率(AA):1年',
       '中债中短期票据到期收益率(AA):3年', '中债中短期票据到期收益率(AA):5年', '中债中短期票据到期收益率(AA):7年',
       '中债中短期票据到期收益率(AA):10年', 'FR007利率互换收盘曲线_均值:1Y', 'FR007利率互换收盘曲线_均值:5Y']
    dt = datetime.now()
    dtPre1 = dt - timedelta(1)
    startdt = datetime(2011,1,1)
    end_dt = dt
    error_code, addData = w.edb("M1000158,M1000160,M1000162,M1000164,M1000166,M1004298,M1004300,M1004302,M1004304,M1004306,M1004263,M1004265,M1004267,M1004269,M1004271,M1000184,M1000186,M1000188,M1000190,M1000192,M1007666,M1007668,M1007670,M1007672,M1007675,M1000532,M1000534,M1000536,M1000538,M1002762,M1000559,M1000561,M1000563,M1002753,M1004359,M1000571,M1000573,M1000575,M1004133,M1004360,M1004104,M1004108",
        dtPre1.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d"), usedf=True)
    if error_code == 0:
        if addData.shape[1] <= 2:
            addData = addData.T
            addData.columns = columns
        # sql = """
        # select 日期 from VarietiesYield where 日期 > %s
        # """

        addData['日期'] = dtPre1.date()
        addData.to_sql("VarietiesYield", engine, if_exists="append", index=False)

        # 计算分位数
        df = pd.read_sql("VarietiesYield", con=engine, index_col='日期')
        df = df.sort_index()
        X = df.values

        baseDate = "2012-01-01"
        startDate = "2014-04-01"
        baseDateIndex = sum(pd.to_datetime(baseDate) > df.index)
        startDateIndex = sum(pd.to_datetime(startDate) > df.index)
        rows, cols = df.shape

        # ComparedPriceMatrix = 1 - ComparedPriceCal1(X, g)
        ComparedPriceMatrix = 1 - ComparedPriceCal1(X, g1)

        # DF = pd.DataFrame(ComparedPriceMatrix[startDateIndex:, :], df.index.values[startDateIndex:])
        DF = pd.DataFrame(ComparedPriceMatrix, df.index.values[-1:])

        # DF.to_excel("C:\\Users\\l_cry\\Desktop\\相对价值计算结果.xlsx")

        DF.columns = df.columns
        DF.to_sql("RelativePriceComparison", engine, if_exists='append', index_label='日期')






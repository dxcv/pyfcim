import pandas as pd
import numpy as np


df = pd.read_excel("C:\\Users\\l_cry\\Desktop\\相对价值计算.xlsx",index_col="日期")
df = df.replace(0,np.nan).fillna(method='ffill')

X = df.values
baseDate = "2006-01-01"

startDate = "2017-04-01"
baseDateIndex = sum(pd.to_datetime(baseDate) > df.index)
startDateIndex = sum(pd.to_datetime(startDate) > df.index)
rows, cols = df.shape

def g(arr, startDateIndex):
    StartIndex = max(startDateIndex, np.isnan(arr).sum())
    return list(map(lambda i : (arr[0,i]>arr[0,baseDateIndex:i]).sum()/(i-baseDateIndex) if i > StartIndex else np.nan, np.arange(0,rows)))


# @jit(nogil=True)
def ComparedPriceCal1(X):
    NanNumArr = np.isnan(X).sum(0)
    XMat = np.matrix(X)
    def h(XMatArr):
        XMat0 = np.apply_along_axis(g, 0, XMatArr.reshape((-1, 1)) - XMat, startDateIndex)
        return (XMat0.sum(1) / (cols - 1))
    XMatNotes = np.apply_along_axis(h, 0 ,XMat)

    return XMatNotes

ComparedPriceMatrix = ComparedPriceCal1(X)

DF = pd.DataFrame(ComparedPriceMatrix[startDateIndex:,:], df.index.values[startDateIndex:])

DF.to_excel("C:\\Users\\l_cry\\Desktop\\相对价值计算结果.xlsx")

(df.iloc[baseDateIndex:,:].apply(lambda x : df.iloc[baseDateIndex:,0]-x, axis=0)).apply(lambda x: sum(x[-1]>x)/x.dropna().__len__()).sum()/(cols-1)



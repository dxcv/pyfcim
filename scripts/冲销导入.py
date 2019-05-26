#%%
import pandas as pd
import pymssql
from sqlalchemy import create_engine
conn = pymssql.connect(host = "192.168.87.73",user = "sa",password = 'tcl+nftx',database = "MarketMaker")
engine = create_engine('mssql+pyodbc://sa:tcl+nftx@192.168.87.73:1433/MarketMaker?driver=SQL+Server')
df = pd.read_excel("C:\\Users\\l_cry\\Desktop\\data\\东海证券股份有限公司_冲销明细20190315.xls")
#%%
def f(code):
    cur = conn.cursor()
    sql = """
    select 本方,本方交易员,对手方,对手方交易员 from IRSTradeDetails where 合约编号 = '%s'
    """ % code
    cur.execute(sql)
    re = cur.fetchone()
    cur.close()
    return re

data = df['成交编号'].apply(f)
for i in range(df.shape[0]):
    re = f(df.loc[i,'成交编号'])
    df.loc[i,'本方'] = re[0]
    df.loc[i,'本方交易员'] = re[1]
    df.loc[i, '对手方'] = re[2]
    df.loc[i, '对手方交易员'] = re[3]


df.to_sql('IRSTradeOffDetails',engine,index=False)


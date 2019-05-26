#%%
import pandas as pd
import pymssql
import numpy as np
from sqlalchemy import create_engine
from datetime import date, timedelta

#%%
conn_43 = pymssql.connect(host="10.28.7.43", user="sa", password='tcl+nftx', database="InvestSystem")

def qualificationCal(calablebonds):
    rankstat = calablebonds['RANK1'].value_counts()
    add1 = rankstat['AAA'] if 'AAA' in rankstat.index.values else 0
    add2 = rankstat['AA'] if 'AA' in rankstat.index.values else 0
    return add1*0.2+add2*(-0.5)


def calableBonds(date):
    sql_calablebonds = """
                select * from openquery(IBOND,'
                select code,name,rank1,category,actualamount, fullmultiple from ibond.view_dh  where category in (''超短融'',''短期融资券'',''中期票据'')
                and issueday <= ''%s'' 
                and paymentday >=''%s''
                ')
        """ % (date[0:4]+'-'+date[4:6]+'-'+date[6:8], date[0:4]+'-'+date[4:6]+'-'+date[6:8])
    calablebonds = pd.read_sql_query(sql_calablebonds, conn_43)
    return calablebonds


def emotionCal(df):
    if df is not None and df.ACTUALAMOUNT.dropna().__len__() > 0:
        df['FULLMULTIPLE'] = df.FULLMULTIPLE.apply(lambda x: x if x is not None else 0.5)
        df.ACTUALAMOUNT = df.ACTUALAMOUNT.apply(lambda x : str2float(x))
        df.FULLMULTIPLE = df.FULLMULTIPLE.apply(lambda x: str2float(x))
        return (df.ACTUALAMOUNT * df.FULLMULTIPLE).dropna().sum()/df.ACTUALAMOUNT.dropna().sum()


def str2float(s):
    try:
        return float(s)
    except:
        return np.nan

def  AAA9M(dt):
    sql = """select * from OPENQUERY(WINDNEW,'
    select t.trade_dt,t.b_anal_yield from CBondCurveCNBD t where t.b_anal_curvename = ''中债企业债收益率曲线(AAA)'' and t.b_anal_curvetype=2  and
     t.b_anal_curveterm=0.75 AND trade_dt=''%s'' ')
    """% (dt)
    cur = conn_43.cursor()
    cur.execute(sql)
    AAA9M_yield = cur.fetchone()
    cur.close()
    return AAA9M_yield

#%%
if __name__ == '__main__':
    # qualificationCal("20190128")
    # publishInfo("101900152.IB")
    engine_InvestSystem = create_engine('mssql+pyodbc://sa:tcl+nftx@10.28.7.43:1433/InvestSystem?driver=SQL+Server')

    # calableBonds('20190128')
    calList = []
    end = date.today().strftime("%Y%m%d")
    date_range = pd.date_range(start=end,end=end,freq='d')
    # date_range = pd.date_range(start="20190101", end="20190306", freq='d')
    for dt in date_range:
    #for Date in tdays.Times:
        df = calableBonds(dt.strftime("%Y%m%d"))
        #AAA9Minfo = AAA9M(Date.strftime("%Y%m%d"))
        # if AAA9Minfo is not None:
        #     calList.append([Date.strftime("%Y%m%d"), qualificationCal(df), emotionCal(df), float(AAA9Minfo[1])])
        #     print(Date.strftime("%Y%m%d"))
    calList.append([dt.strftime("%Y%m%d"), qualificationCal(df), emotionCal(df), np.nan])
    if calList.__len__() > 0:
        df = pd.DataFrame(calList, columns=['updatetime', 'qualification', 'emotion', 'AAA9MYield'])
        df[['updatetime', 'qualification']].to_sql("QualificationIndex", engine_InvestSystem, index=False, if_exists='append')
        #df[['updatetime', 'emotion', 'AAA9MYield']].to_sql("EmotionIndex", engine_InvestSystem, index=False, if_exists='append')

    print("finished")

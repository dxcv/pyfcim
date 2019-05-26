
from CRMCal.QualificationEmotionCalat1800 import *

#%%
if __name__ == '__main__':
    # qualificationCal("20190128")
    # publishInfo("101900152.IB")
    engine_InvestSystem = create_engine('mssql+pyodbc://sa:tcl+nftx@10.28.7.43:1433/InvestSystem?driver=SQL+Server')

    # calableBonds('20190128')
    calList = []
    end = date.today().strftime("%Y%m%d")
    start = (date.today()-timedelta(14)).strftime("%Y%m%d")
    cur = conn_43.cursor()
    sql = """
            delete from EmotionIndex where updatetime >= '%s';
            delete from QualificationIndex where updatetime >= '%s';
    """ % (start, start)
    cur.execute(sql)
    conn_43.commit()
    cur.close()

    date_range = pd.date_range(start=start, end=end, freq='d')
    # date_range = pd.date_range(start="20190101", end="20190306", freq='d')
    for dt in date_range:
    #for Date in tdays.Times:
        df = calableBonds(dt.strftime("%Y%m%d"))
        # AAA9Minfo = AAA9M(Date.strftime("%Y%m%d"))
        # if AAA9Minfo is not None:
        #     calList.append([Date.strftime("%Y%m%d"), qualificationCal(df), emotionCal(df), float(AAA9Minfo[1])])
        #     print(Date.strftime("%Y%m%d"))
        calList.append([dt.strftime("%Y%m%d"), qualificationCal(df), emotionCal(df), np.nan])

    if calList.__len__() > 0:
        df = pd.DataFrame(calList, columns=['updatetime', 'qualification', 'emotion', 'AAA9MYield'])
        df[['updatetime', 'qualification']].to_sql("QualificationIndex", engine_InvestSystem, index=False, if_exists='append')
        df[['updatetime', 'emotion', 'AAA9MYield']].to_sql("EmotionIndex", engine_InvestSystem, index=False, if_exists='append')

    print("finished")

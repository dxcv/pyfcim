#%%
import pandas as pd
from model.Database_config import conn_43,engine_103
from datetime import timedelta
from model.DataReg import is_outlier
import numpy as np

def fetch_future_price(bondCode, start_time, end_time):
    sql = """
    select * from data_reg.dbo.FutureHQ_reg where SCode = '%s' and updatetime > '%s'
    and updatetime <= '%s'
    """%(bondCode, start_time, end_time)
    return pd.read_sql_query(sql, engine_103)


def fetch_QBBBO_cleanprice(bondCode, start_time,end_time):
    sql = """
    select * from data_reg.dbo.QBBBO_history_reg1 where bondCode = '%s' and createDateTime > '%s'
    and createDateTime <= '%s'
    """%(bondCode, start_time, end_time)
    return pd.read_sql_query(sql, engine_103)


def diff(code1, code2, start_time,end_time,cf=1):
    date_range = pd.date_range(start=start_time, end=end_time, freq='d')
    df_notes = pd.DataFrame(columns=('updatetime','diff'))
    for left in date_range[:-1]:
        am_left = left.strftime("%Y-%m-%d")+" 9:15:00"
        am_right = left.strftime("%Y-%m-%d")+" 11:30:00"

        pm_left = left.strftime("%Y-%m-%d")+" 13:00:00"
        pm_right = left.strftime("%Y-%m-%d") + " 15:15:00"
        code1_type = code1.split(".")[1]
        code2_type = code2.split(".")[1]
        if code1_type == "ZJ":
            df1 = pd.concat([fetch_future_price(code1, am_left, am_right), fetch_future_price(code1,
                                                                                                      pm_left, pm_right)], axis=0)
        else:
            df1 = pd.concat([fetch_QBBBO_cleanprice(code1, am_left, am_right), fetch_QBBBO_cleanprice(code1,
                                                                                                      pm_left, pm_right)], axis=0)
        if code2_type == "ZJ":
            df2 = pd.concat([fetch_future_price(code2, am_left, am_right), fetch_future_price(code2,
                                                                                                      pm_left, pm_right)], axis=0)
        else:
            df2 = pd.concat([fetch_QBBBO_cleanprice(code2, am_left, am_right), fetch_QBBBO_cleanprice(code2,
                                                                                                      pm_left, pm_right)], axis=0)                                                                                              
        if code1_type == "ZJ":
            if code2_type == "IB":
                df = pd.merge(df1,df2,how='left', left_on='updatetime', right_on='createDateTime')
                df['diff'] = ((df.BuyPrice1+df.SellPrice1)/2)*cf - (df.last_bid_cleanprice+df.last_ofr_cleanprice)/2
                df_notes = df_notes.append(df.sort_values(by='updatetime'))
            if code2_type == "ZJ":
                df = pd.merge(df1,df2,how='left', left_on='updatetime', right_on='updatetime')
                df['diff'] = (df.BuyPrice1_x+df.SellPrice1_x)/2*cf - (df.BuyPrice1_y+df.SellPrice1_y)/2
                df_notes = df_notes.append(df.sort_values(by='updatetime'))
        elif code1_type == "IB":
            if code2_type == "ZJ":
                print("请将ZJ代码前置后重置")
            elif code2_type == "IB":
                df = pd.merge(df1,df2,how='left', left_on='createDateTime', right_on='createDateTime')
                df['diff'] = (df.last_bid_cleanprice_x+df.last_ofr_cleanprice_x)/2*cf - (df.last_bid_cleanprice_y+df.last_ofr_cleanprice_y)/2
                df_notes = df_notes.append(df.sort_values(by='createDateTime'))
    return df_notes

def price_diff_ZJ_IB(Scode, bondCode, start_time, end_time, cf=1):
    sql="""
    SELECT
	A.SCode,
	B.bondCode,
	CASE WHEN A.BuyPrice1 = 0 THEN NULL ELSE A.BuyPrice1 END AS BuyPrice1,
	CASE WHEN A.SellPrice1 = 0 THEN NULL ELSE 	A.SellPrice1 END AS SellPrice1,
	B.last_bid_cleanprice,
	B.last_ofr_cleanprice,
	(CASE WHEN A.BuyPrice1 = 0 THEN NULL ELSE A.BuyPrice1 END +CASE WHEN A.SellPrice1 = 0 THEN NULL ELSE 	A.SellPrice1 END )/2*%d - (B.last_bid_cleanprice+b.last_ofr_cleanprice)/2 as mid_diff,
	A.updatetime
    FROM
	    FutureHQ_reg A
        LEFT JOIN QBBBO_history_reg1 B ON A.updatetime = B.createDateTime
    WHERE
        A.SCode = '%s'
        AND B.bondCode = '%s'
        AND A.updatetime > '%s'
        AND A.updatetime <= '%s'
    ORDER BY
        A.updatetime
    """%(cf, Scode, bondCode, start_time, end_time)
    df = pd.read_sql_query(sql,engine_103)
    # 数据清洗，去除掉三个标准差以外的数值
    df.loc[is_outlier(df['mid_diff'].values) == 1, 'mid_diff'] = np.NaN
    return df

def price_diff_IB_IB(bondCode1, bondCode2, start_time, end_time, cf=1):
    sql = """
    SELECT
	A.bondCode bondCode1,
	A.last_bid_cleanprice bondCode1_last_bid_cleanprice,
	A.last_ofr_cleanprice bondCode1_last_ofr_cleanprice,
    A.last_bid bondCode1_last_bid, 
	A.last_ofr bondCode1_last_ofr,
	B.bondCode bondCode2,
	B.last_bid_cleanprice bondCode2_last_bid_cleanprice,
	B.last_ofr_cleanprice bondCode2_last_ofr_cleanprice,
    B.last_bid bondCode2_last_bid, 
	B.last_ofr bondCode2_last_ofr,
	--价差取bid,ofr和sell,buy的中间价
	(A.last_bid_cleanprice+A.last_ofr_cleanprice)/2*%d - (B.last_bid_cleanprice+B.last_ofr_cleanprice)/2 as cleanprice_mid_diff,
	(A.last_bid+A.last_ofr)/2 - (B.last_bid+B.last_ofr)/2 as yield_mid_diff,
	A.createDateTime
    FROM
        QBBBO_history_reg1 A
    LEFT JOIN QBBBO_history_reg1 B ON A.createDateTime = B.createDateTime
    WHERE
        A.bondCode = '%s' --债券名
    AND B.bondCode = '%s' --债券名
    AND A.createDateTime > '%s'  --起始时间
    AND A.createDateTime <= '%s' --结束时间
    ORDER BY
        A.createDateTime
    """%(cf, bondCode1, bondCode2, start_time, end_time)
    df = pd.read_sql_query(sql, engine_103)
    ## 数据清洗
    df.loc[is_outlier(df['cleanprice_mid_diff'].values) == 1,'cleanprice_mid_diff'] = np.NaN
    df.loc[is_outlier(df['yield_mid_diff'].values) == 1, 'yield_mid_diff'] = np.NaN
    return df

def price_diff_ZJ_ZJ(SCode1, Scode2, start_time, end_time, cf=1):
    sql="""
    SELECT
        A.SCode SCode1,
        CASE WHEN A.BuyPrice1 = 0 THEN NULL ELSE A.BuyPrice1 END AS SCode1_BuyPrice1,
        CASE WHEN A.SellPrice1 = 0 THEN NULL ELSE 	A.SellPrice1 END AS SCode1_SellPrice1,
        B.SCode Scode2,
        CASE WHEN B.BuyPrice1 = 0 THEN NULL ELSE B.BuyPrice1 END AS SCode2_BuyPrice1,
        CASE WHEN B.SellPrice1 = 0 THEN NULL ELSE 	B.SellPrice1 END AS SCode2_SellPrice1,
        --价差取bid,ofr和sell,buy的中间价
        (CASE WHEN A.BuyPrice1 = 0 THEN NULL ELSE A.BuyPrice1 END +CASE WHEN A.SellPrice1 = 0 THEN NULL ELSE A.SellPrice1 END )/2*%d - (CASE WHEN B.BuyPrice1 = 0 THEN NULL ELSE B.BuyPrice1 END +CASE WHEN B.SellPrice1 = 0 THEN NULL ELSE B.SellPrice1 END )/2 as mid_diff,
        A.updatetime
    FROM
        FutureHQ_reg A
    LEFT JOIN FutureHQ_reg B ON A.updatetime = B.updatetime
    WHERE
        A.SCode = '%s' --期货代码

    AND B.SCode = '%s' --债券名
    AND A.updatetime > '%s'  --起始时间
    AND A.updatetime <= '%s' --结束时间
    ORDER BY
        A.updatetime
    """(cf, SCode1, Scode2, start_time, end_time)
    df = pd.read_sql_query(sql, engine_103)
    # 去除掉3个标准差以外的数值
    df.loc[is_outlier(df['mid_diff'].values) == 1, 'mid_diff'] = np.NaN
    return df

#%%
# df = price_diff_ZJ_IB('TF1812.ZJ', '180023.IB', '20181115','20181206')
# df.head()

#%%

# SCode_pool = ("T1903.ZJ","TF1903.ZJ")
# bond_pool = ('180013.IB','180023.IB','180016.IB','180015.IB','180214.IB','180204.IB','170215.IB','170210.IB',
#          '180011.IB','180209.IB', '180208.IB', '180211.IB', '180210.IB', '180206.IB', '180212.IB' ,
#         	'180304.IB','180309.IB','180313.IB','180406.IB','180010.IB','180019.IB','180205.IB')

# pair_gen = ((SCode,bond) for SCode in SCode_pool for bond in bond_pool)

# df = price_diff_IB_IB('180210.IB','180205.IB','20181201','20181224')
if __name__=="__main__":
    def todbbyday(start_time, end_time, SCode_pool, bond_pool, cf=1):
        pair_gen = ((SCode,bond) for SCode in SCode_pool for bond in bond_pool)
        def get_data(code1, code2):
            df = price_diff_ZJ_IB(code1, code2, start_time, end_time, cf=1)
            df.to_sql("price_diff_ZJ_IB",con=engine_103, if_exists="append", index=False, chunksize=4000)
            print(code1+","+code2+"价差已录入")
        for x1,x2 in pair_gen:
            get_data(x1,x2)
        print(start_time+"价差已录入")


    #%%

    # todbbyday('20181115','20181116')
    def todbperiod(start_time, end_time, SCode_pool, bond_pool):
        date_range = pd.date_range(start=start_time,end=end_time,freq="d")
        for date in date_range:
            todbbyday(date.strftime("%Y%m%d"),(date+timedelta(1)).strftime("%Y%m%d"), SCode_pool, bond_pool)
        return "Done"

    #todbperiod("20181008", "20181210", SCode_pool, bond_pool)


















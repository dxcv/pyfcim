import pandas as pd
from model.Database_config import conn_43, engine_103
import numpy as np

# 判断字符串是否可数字化
def is_eff_number(s):
    if type(s) is str:
        s_list = s.strip().split('.')
        if len(s_list) == 2 and s_list[0].isdigit() and s_list[1].isdigit():
            return True
        else:
            return False
    else:
        return False

# 将可以数字化的字符串数字化
def str2float(s):
    if is_eff_number(s):
        return float(s)
    else:
        return np.nan


###
# 前几分钟交易的所有券以及交易量
def selectDebtOnTrade(start, end):
    sql = """
            SELECT * FROM QBTRADEVIEW 
            WHERE dealtime > '%s' AND
            dealtime <= '%s'
            """ % (start, end)

    df = pd.read_sql(sql, con=conn_43)
    return df


    code_counts = df.code.value_counts(ascending=False)

    df.groupby('code').apply(lambda df: df['yield'].apply(str2float).dropna().mean())

# 获取债券的基本信息
# S_INFO_WINDCODE 债券代码
# B_TENDRST_REFERYIELD 参考收益率
def getDebtInfo(bondCode):
    sql_wind = """
                SELECT
                	*
                FROM
                	OPENQUERY (
                		WINDNEW,
                		'select S_INFO_WINDCODE,B_ISSUE_FIRSTISSUE,B_INFO_FULLNAME,B_INFO_COUPONRATE,B_INFO_INTERESTFREQUENCY,
                        B_INFO_CARRYDATE,B_INFO_ENDDATE,B_INFO_MATURITYDATE,B_INFO_TERM_YEAR_,B_INFO_COUPONDATETXT,
                        B_INFO_ACTUALBENCHMARK,B_INFO_SUBORDINATEORNOT,B_TENDRST_REFERYIELD
                 from CBondDescription where S_INFO_WINDCODE = ''%s'' '
                	)
                """ % bondCode
    cur = conn_43.cursor()
    cur.execute(sql_wind)
    debt_info = cur.fetchone()
    return debt_info

# 获得债券的中债估值
# 债券剩余期、中债估值、日终收益率、
def getDebtCNBD(bondCode, datetime):
    sql_CNBD = """
                SELECT
                *
                FROM
                OPENQUERY (
                    WINDNEW,
                    'select * from CBondAnalysisCNBD where s_info_windcode=''%s'')  and trade_dt = ''%s'''
                )
                """% bondCode, datetime

    cur = conn_43.cursor()
    cur.execute(sql_CNBD)
    CNBD_info = cur.fetchone()
    return CNBD_info


if __name__ == '__main__':

    selectDebtOnTrade('20190117 00:00:00')









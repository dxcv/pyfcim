
from model.pair_config import debt_info,debt_map,debt_name_trans
from model.CleanPriceDiff import price_diff_IB_IB,price_diff_ZJ_IB
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from model.Database_config import engine_103

datenow = datetime.now()
start_time  = (datenow-timedelta(7)).strftime("%Y%m%d")
end_time = datenow.strftime("%Y%m%d")
columns=['code1','ref1','coff1','code2','ref2','coff2','latestcp','avgcp','stdcp','percentilecp',
'latestyield','avgyield','stdyield','percentileyield']

to_db_list=[]
def trans_name(x):
    x_list = x.split("_")
    return debt_name_trans[x_list[0]]+x_list[1]+"年"+debt_name_trans[x_list[2]]

for names in debt_map.keys():
    pairs = debt_map[names]
    for pairkey in pairs.keys():
        if pairs[pairkey] != -1:
            if pairkey[0].split("_")[0]=='NDF' and pairkey[1].split("_")[1] != "NDF":
                if len(pairkey)==2:
                    df = price_diff_ZJ_IB(pairs[pairkey][0],pairs[pairkey][1],start_time,end_time)
                else:
                    df = price_diff_ZJ_IB(pairs[pairkey][0],pairs[pairkey][1],start_time,end_time,cf=pairkey[2])
                if df.shape[0] == 0:
                    continue
                latestvalue = df.mid_diff.dropna().iloc[-1] if df.mid_diff.dropna().shape[0]>0 else np.NaN
                diff_avg = df.mid_diff.dropna().mean()
                diff_std = df.mid_diff.dropna().std()
                diff_percentile = sum(df.mid_diff.dropna()<latestvalue)/df.mid_diff.dropna().count() if latestvalue is not np.NaN else np.NaN
                to_db_list.append([trans_name(pairkey[0]),pairs[pairkey][0],1 if len(pairkey)==2 else pairkey[2],
                trans_name(pairkey[1]),pairs[pairkey][1],1 if len(pairkey)==2 else pairkey[2],
                latestvalue,diff_avg,diff_std,diff_percentile])

            else:
                if len(pairkey)==2:
                    df = price_diff_IB_IB(pairs[pairkey][0],pairs[pairkey][1],start_time,end_time)
                else:
                    df = price_diff_IB_IB(pairs[pairkey][0],pairs[pairkey][1],start_time,end_time,cf=pairkey[2])
                if df.shape[0] == 0:
                    continue
                latestvalue = df.cleanprice_mid_diff.dropna().iloc[-1] if df.cleanprice_mid_diff.dropna().shape[0]>0 else np.NaN
                diff_avg = df.cleanprice_mid_diff.dropna().mean()
                diff_std = df.cleanprice_mid_diff.dropna().std()
                diff_percentile = sum(df.cleanprice_mid_diff.dropna()<latestvalue)/df.cleanprice_mid_diff.dropna().count() if latestvalue is not np.NaN else np.NaN
                
                latestyield = df.yield_mid_diff.dropna().iloc[-1] if df.yield_mid_diff.dropna().shape[0]>0 else np.NaN
                yield_diff_avg = df.yield_mid_diff.dropna().mean()
                yield_diff_std = df.yield_mid_diff.dropna().std()
                yield_diff_percentile = sum(df.yield_mid_diff.dropna()<latestyield)/df.yield_mid_diff.dropna().count() if latestyield is not np.NaN else np.NaN
                to_db_list.append([trans_name(pairkey[0]),pairs[pairkey][0],1 if len(pairkey)==2 else pairkey[2],
                trans_name(pairkey[1]),pairs[pairkey][1],1 if len(pairkey)==2 else pairkey[3],
                latestvalue,diff_avg,diff_std,diff_percentile,
                latestyield,yield_diff_avg,yield_diff_std,yield_diff_percentile])

df_todb = pd.DataFrame(to_db_list,columns=columns)
df_todb['updatetime'] = datenow.date()
df_todb.to_sql('price_diff',con=engine_103, if_exists="append", index=False, chunksize=4000)


# 债券信息，各券种主连、次新表
debt_info_list=[]
for type1 in debt_info.keys():
    sub_info = debt_info[type1]
    for maturity in sub_info.keys():
        debt_info_list.append([debt_name_trans[type1],maturity]+sub_info[maturity])
debt_info_columns = ['cate','maturity','master','sub'] 
debt_info_df = pd.DataFrame(debt_info_list,columns=debt_info_columns)
debt_info_df['updatetime'] = datenow.date()
debt_info_df.to_sql('debt_info',con=engine_103, if_exists="append", index=False, chunksize=4000)

# 债券信息对应表 
debt_map_list=[]
for type1 in debt_map.keys():
    sub_map = debt_map[type1]
    for pair in sub_map.keys():
        if sub_map[pair] != -1:
            debt_map_list.append([trans_name(pair[0]),trans_name(pair[1]),sub_map[pair][0],sub_map[pair][1]])
debt_map_columns = ['code1','code2','instance1','instance2'] 
debt_map_df = pd.DataFrame(debt_map_list,columns=debt_map_columns)
debt_map_df['updatetime'] = datenow.date()
debt_map_df.to_sql('debt_map',con=engine_103, if_exists="append", index=False, chunksize=4000)

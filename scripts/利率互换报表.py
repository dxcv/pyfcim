import pandas as pd
import numpy as np
from datetime import datetime

dfTradeDetail = pd.read_excel("F:\\利率互换\\利率互换-本方成交明细.xlsx")
dfOffDetail = pd.read_excel("F:\\利率互换\\利率互换-冲销明细.xlsx")
dfResidueDetail = pd.read_excel("F:\\利率互换\\利率互换-估值存量明细.xlsx")

# 预定义
Year = 2019
Month = 4
CurrentMonth = datetime(Year,Month,1)
CurrentYear = datetime(Year,1,1)


# E1_8_2证券公司参与利率互换交易专项监管报表-明细
DF2 = pd.DataFrame(columns=[['序号','交易对手','本月交易情况','本月交易情况','本月交易情况','本月交易情况','期末持仓合约','期末持仓合约','期末持仓合约','期末持仓合约','期末持仓合约','期末持仓合约','期末持仓合约','期末持仓合约','期末持仓合约','本年累计交易情况','本年累计交易情况','本年累计交易情况','本年累计交易情况'],
                            ['','','收固定付浮动合约名义本金','收浮动付固定合约名义本金','其他形式合约名义本金','本月已实现损益 注1','收固定付浮动合约名义本金','收固定付浮动合约价值','收浮动付固定合约名义本金','收浮动付固定合约价值','其他形式合约名义本金','其他形式合约价值','已有效对冲风险的合约名义本金 注2','已有效对冲风险的合约价值 注2','期末持仓合约未实现损益 注3','收固定付浮动合约名义本金','收浮动付固定合约名义本金','其他形式合约名义本金','本年累计已实现损益 注1']
                            ])

DF2['交易对手'] = list(set(dfTradeDetail['对手方'].unique()) | set(dfResidueDetail['对手方'].unique()))
DF2['序号'] = [ i+1 for i in range(DF2['交易对手'].shape[0])]
DF2[('本月交易情况','收固定付浮动合约名义本金')] = DF2['交易对手'].apply(lambda x: sum(dfTradeDetail[(dfTradeDetail['对手方']==x) & (dfTradeDetail['交易方向']=='收取固定利率') & (dfTradeDetail['成交时间'] >= CurrentMonth )]['名义本金额(万元)']))
DF2[('本月交易情况','收浮动付固定合约名义本金')] = DF2['交易对手'].apply(lambda x: sum(dfTradeDetail[(dfTradeDetail['对手方']==x) & (dfTradeDetail['交易方向']=='支付固定利率') & (dfTradeDetail['成交时间'] >= CurrentMonth )]['名义本金额(万元)']))
DF2[('本月交易情况','本月已实现损益 注1')] = DF2['交易对手'].apply(lambda x: sum(dfOffDetail[(dfOffDetail['对手方']==x) & (dfOffDetail['操作时间'] >= CurrentMonth )]['冲销估值（元）']))

DF2[('期末持仓合约','收固定付浮动合约名义本金')] = DF2['交易对手'].apply(lambda x: sum(dfResidueDetail[(dfResidueDetail['对手方']==x) & (dfResidueDetail['交易方向']=='收取固定')]['剩余名义本金（万元）']))
DF2[('期末持仓合约','收固定付浮动合约价值')] = DF2['交易对手'].apply(lambda x: sum(dfResidueDetail[(dfResidueDetail['对手方']==x) & (dfResidueDetail['交易方向']=='收取固定')]['估值（元）（T+1）']))
DF2[('期末持仓合约','收浮动付固定合约名义本金')] = DF2['交易对手'].apply(lambda x: sum(dfResidueDetail[(dfResidueDetail['对手方']==x) & (dfResidueDetail['交易方向']=='支付固定')]['剩余名义本金（万元）']))
DF2[('期末持仓合约','收浮动付固定合约价值')] = DF2['交易对手'].apply(lambda x: sum(dfResidueDetail[(dfResidueDetail['对手方']==x) & (dfResidueDetail['交易方向']=='支付固定')]['估值（元）（T+1）']))
DF2[('期末持仓合约','期末持仓合约未实现损益 注3')] = DF2[('期末持仓合约','收固定付浮动合约价值')] + DF2[('期末持仓合约','收浮动付固定合约价值')]

DF2[('本年累计交易情况','收固定付浮动合约名义本金')] = DF2['交易对手'].apply(lambda x: sum(dfTradeDetail[(dfTradeDetail['对手方']==x) & (dfTradeDetail['交易方向']=='收取固定利率') & (dfTradeDetail['成交时间'] >= CurrentYear )]['名义本金额(万元)']))
DF2[('本年累计交易情况','收浮动付固定合约名义本金')] = DF2['交易对手'].apply(lambda x: sum(dfTradeDetail[(dfTradeDetail['对手方']==x) & (dfTradeDetail['交易方向']=='支付固定利率') & (dfTradeDetail['成交时间'] >= CurrentYear )]['名义本金额(万元)']))
DF2[('本年累计交易情况','本年已实现损益 注1')] = DF2['交易对手'].apply(lambda x: sum(dfOffDetail[(dfOffDetail['对手方']==x) & (dfOffDetail['操作时间'] >= CurrentYear )]['冲销估值（元）']))

# DF2[[('对手方',''),('期末持仓合约','期末持仓合约未实现损益 注3')]]

# E1_8_1证券公司参与利率互换交易专项监管报表-明细
DF1 = pd.DataFrame(columns=[['序号','交易日期','固定利息支付方','浮动利息支付方','名义本金（万元）','合约期限','起息日','到期日','固定利率','固定利率','固定利率','浮动利率','浮动利率','浮动利率','首次利息支付（互换）日'],
                            ['','','','','','','','','利率（%）','支付频率','计息基准','利率（%）','支付频率','计息基准','']
                            ])

DF1[('名义本金（万元）','')] = dfResidueDetail['剩余名义本金（万元）']
DF1['序号'] = [i+1 for i in range(dfResidueDetail.shape[0])]
DF1[('固定利息支付方','')] = dfResidueDetail[['对手方','交易方向']].apply(lambda row : '东海证券' if row['交易方向']=='支付固定' else row['对手方'], axis=1)
DF1[('浮动利息支付方','')] = dfResidueDetail[['对手方','交易方向']].apply(lambda row : row['对手方'] if row['交易方向']=='支付固定' else '东海证券',axis=1)
DF1[('合约期限','')] = dfResidueDetail['期限品种']
DF1[('起息日','')] = dfResidueDetail['起息日']
DF1[('到期日','')] = dfResidueDetail['到期日']
DF1[('固定利率','利率（%）')] = dfResidueDetail['固定利率（%）']
DF1[('固定利率','支付频率')] = dfResidueDetail['固定利率支付频率'].apply(lambda x: x.replace("季","每季度"))
DF1[('固定利率','计息基准')] = dfResidueDetail['固定利率计息基准'].apply(lambda x: x.replace("实际","A"))
DF1[('浮动利率', '利率（%）')] = dfResidueDetail['参考利率']
DF1[('浮动利率', '支付频率')] = dfResidueDetail['浮动利率支付频率'].apply(lambda x: x.replace("季","每季度"))
DF1[('浮动利率', '计息基准')] = dfResidueDetail['浮动利率计息基准'].apply(lambda x: x.replace("实际","A"))
DF1[('首次利息支付（互换）日','')] = dfResidueDetail['合约编号'].apply(lambda x: dfTradeDetail.loc[dfTradeDetail['成交编号'] == x,'初始支付日-固定利率方'].values[0])
DF1[('交易日期','')] = dfResidueDetail['合约编号'].apply(lambda x: dfTradeDetail.loc[dfTradeDetail['成交编号'] == x,'成交时间'].values[0])

#NAFMII月报-业务统计
NADF1 = pd.DataFrame(columns=['协议类别','上月末本年累计','本月新增','本年累计','本月末有效'])
NADF1['协议类别'] = ['主协议','补充协议','履约保障协议','交易确认书']
NADF1 = NADF1.fillna(0)
NADF1.loc[0,'上月末本年累计'] = (CurrentYear<=dfTradeDetail["成交时间"]<CurrentMonth).sum()
NADF1.loc[0,'本月新增'] = (dfTradeDetail["成交时间"]>=CurrentMonth).sum()
NADF1.loc[0,'本月末有效'] = dfResidueDetail.shape[0]

# 交易确认书
NADF1.loc[3,'上月末本年累计'] = NADF1.loc[0:2,'上月末本年累计'].sum()
NADF1.loc[3,'本月新增'] = NADF1.loc[0:2,'本月新增'].sum()
NADF1.loc[3,'本月末有效'] = NADF1.loc[0:2,'本月末有效'].sum()
# 计算本年累计
NADF1['本年累计'] = NADF1['上月末本年累计'] + NADF1['本月新增']

# 业务规模统计
NADF12 = pd.DataFrame(columns=[['标的类型','名义本金（亿元）（小数点后两位小数）','名义本金（亿元）（小数点后两位小数）',
                                '名义本金（亿元）（小数点后两位小数）','名义本金（亿元）（小数点后两位小数）','名义本金（亿元）（小数点后两位小数）',
                                '合约笔数（笔）','合约笔数（笔）','合约笔数（笔）','合约笔数（笔）','合约笔数（笔）'
                                ],
                               ['','本月初存续交易','本月新增交易','本月了结交易','本月末存续交易','截至本月末年度新增交易',
                                '本月初存续交易','本月新增交易','本月了结交易','本月末存续交易','截至本月末年度新增交易']
                               ])
NADF12['标的类型'] = ['利率', '黄金', '外汇', '其他', '合计']
NADF12 = NADF12.fillna(0)
# 利率
NADF12.loc[0,('名义本金（亿元）（小数点后两位小数）', '本月新增交易')] = dfTradeDetail[dfTradeDetail['成交时间'] >= CurrentMonth]['名义本金额(万元)'].sum()/10000 # /10000单位换算
NADF12.loc[0,('名义本金（亿元）（小数点后两位小数）', '本月了结交易')] = dfOffDetail[dfOffDetail['操作时间'] >= CurrentMonth]['原剩余名义本金（万元）'].sum()/10000
NADF12.loc[0,('名义本金（亿元）（小数点后两位小数）', '本月末存续交易')] = dfResidueDetail['剩余名义本金（万元）'].sum()/10000
NADF12.loc[0,('名义本金（亿元）（小数点后两位小数）', '截至本月末年度新增交易')] = dfTradeDetail[dfTradeDetail['成交时间'] >= CurrentYear]['名义本金额(万元)'].sum()/10000

NADF12.loc[0,('合约笔数（笔）', '本月新增交易')] = (dfTradeDetail['成交时间'] >= CurrentMonth).sum() # /10000单位换算
NADF12.loc[0,('合约笔数（笔）', '本月了结交易')] = (dfOffDetail['操作时间'] >= CurrentMonth).sum()
NADF12.loc[0,('合约笔数（笔）', '本月末存续交易')] = dfResidueDetail.shape[0]
NADF12.loc[0,('合约笔数（笔）', '截至本月末年度新增交易')] = (dfTradeDetail['成交时间'] >= CurrentYear).sum()

# 合计
NADF12.loc[4,('名义本金（亿元）（小数点后两位小数）', '本月新增交易')] = NADF12.loc[0:3,('名义本金（亿元）（小数点后两位小数）', '本月新增交易')].sum()
NADF12.loc[4,('名义本金（亿元）（小数点后两位小数）', '本月了结交易')] = NADF12.loc[0:3,('名义本金（亿元）（小数点后两位小数）', '本月了结交易')].sum()
NADF12.loc[4,('名义本金（亿元）（小数点后两位小数）', '本月末存续交易')] = NADF12.loc[0:3,('名义本金（亿元）（小数点后两位小数）', '本月末存续交易')].sum()
NADF12.loc[4,('名义本金（亿元）（小数点后两位小数）', '截至本月末年度新增交易')] = NADF12.loc[0:3,('名义本金（亿元）（小数点后两位小数）', '截至本月末年度新增交易') ].sum()
NADF12.loc[4,('合约笔数（笔）', '本月新增交易')] = NADF12.loc[0:3,('合约笔数（笔）', '本月新增交易')].sum()
NADF12.loc[4,('合约笔数（笔）', '本月了结交易')] = NADF12.loc[0:3,('合约笔数（笔）', '本月了结交易')].sum()
NADF12.loc[4,('合约笔数（笔）', '本月末存续交易')] = NADF12.loc[0:3,('合约笔数（笔）', '本月末存续交易')].sum()
NADF12.loc[4,('合约笔数（笔）', '截至本月末年度新增交易')] = NADF12.loc[0:3,('合约笔数（笔）', '截至本月末年度新增交易')].sum()

# 当月的流水明细
NADF2 = pd.DataFrame(columns=[['序号','交易日期','填报机构名称','填报机构代签产品名称','交易对手方名称','交易对手方代签产品名称','交易对手方类型',
                               '交易对手是否为专业机构','固定利息支付方（机构名称）','浮动利息支付方（机构名称）','名义本金（亿元）','合约期限（天）','起息日','到期日',
                               '固定利率','固定利率','固定利率','浮动利率','浮动利率','浮动利率','浮动利率','浮动利率','首次利息支付（互换）日'],
                              ['','','','','','','','','','','','','','','利率（%）','支付周期','计息基准','参考利率名称','利差（bps）','支付周期','重置频率','计息基准','']
                              ])
temp = dfTradeDetail[dfTradeDetail['成交时间']>=CurrentMonth]
if temp.shape[0] >= 1:
    NADF2[('交易日期', '')] = temp['成交时间']
    NADF2['填报机构名称'] = '东海证券'
    NADF2['交易对手方名称'] = temp['对手方']
    NADF2['交易对手方类型'] = temp['对手方'].apply(lambda x: '07' if '银行' in x else '01' if '证券' in x else '')
    NADF2['交易对手是否为专业机构'] = '01'
    NADF2['固定利息支付方（机构名称）'] = temp[['对手方','交易方向']].apply(lambda row : '东海证券' if row['交易方向']=='支付固定利率' else row['对手方'],axis=1)
    NADF2['浮动利息支付方（机构名称）'] = temp[['对手方','交易方向']].apply(lambda row : row['对手方'] if row['交易方向']=='支付固定利率' else '东海证券' ,axis=1)
    NADF2['名义本金（亿元）'] = temp['名义本金额(万元)']/10000
    NADF2[('起息日','')] = temp['起息日']
    NADF2[('到期日','')] = temp['到期日']
    NADF2[('合约期限（天）','')] = temp[['起息日','到期日']].apply(lambda row : pd.to_datetime(row['到期日'])-pd.to_datetime(row['起息日']), axis=1).apply(lambda x:x.days)
    NADF2[('固定利率','支付周期')] = temp['固定利率支付周期'].apply(lambda x: x.replace("季","每季度"))
    NADF2[('固定利率','计息基准')] = temp['固定利率计息基准'].apply(lambda x: x.replace("实际","A"))
    NADF2[('浮动利率', '参考利率名称')] = temp['参考利率']
    NADF2[('浮动利率', '利差（bps）')] = 0
    NADF2[('浮动利率', '支付周期')] = temp['浮动利率支付周期'].apply(lambda x: x.replace("季","每季度"))
    NADF2[('浮动利率', '计息基准')] = temp['浮动利率计息基准'].apply(lambda x: x.replace("实际","A"))
    NADF2[('首次利息支付（互换）日','')] = temp['初始支付日-固定利率方']
    NADF2['序号'] = [i+1 for i in range(temp.shape[0])]


# 写入Excel中
DFWriter = pd.ExcelWriter("利率互换专项报表_东海证券.xlsx")
DF1.to_excel(DFWriter, sheet_name = 'E1_8_1证券公司参与利率互换交易专项监管报表-明细')
DF2.to_excel(DFWriter, sheet_name = 'E1_8_2证券公司参与利率互换交易专项监管报表-明细')
DFWriter.close()

NADFWriter = pd.ExcelWriter("NAFMII月报.xlsx")
NADF1.to_excel(NADFWriter, sheet_name='签署协议统计')
NADF12.to_excel(NADFWriter, sheet_name='业务规模统计')
NADF2.to_excel(NADFWriter, sheet_name='利率互换明细')
NADFWriter.close()




# import pandas as pd
# import pymssql
# dfList =[]
# codelist = ["180217","160219","140226","120252","120250","120251","110256","110255","090214","090213","090215","050210","040224","180322","180321"]
# conn_43 = pymssql.connect(host = "10.28.7.43",user = "bond",password = 'bond',database = "qbdb")
# for item in codelist:
#     sql = """SELECT * FROM openquery(TEST,'select  DEALBONDNAME,DEALBONDCODE, DEALCLEANPRICE, DEALYIELD, DEALTOTALFACEVALUE/10000 DEALTOTALFACEVALUE,TRADEMETHOD, TRANSACTTIME from marketanalysis.CMDSCBMDEALT where DEALBONDCODE=''%s''' )""" % item
#     dfList.append(pd.read_sql(sql,conn_43))
# DFWriter = pd.ExcelWriter("银行间交易记录.xlsx")
# for i in range(15):
#     dfList[i].to_excel(DFWriter, sheet_name=codelist[i])
# DFWriter.close()
# i=0
# dfList[i].to_excel("test.xlsx", sheet_name=codelist[i])

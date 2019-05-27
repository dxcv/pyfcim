# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 14:41:16 2018

@author: l_cry
"""
import sys
sys.path.append("../")
import pandas as pd
import pymssql
import numpy as np
import datetime
from sqlalchemy import create_engine
from data.BondCalc import BondCalc


class QBdata:
    # 数据库配置
    conn_43 = pymssql.connect(host="10.28.7.43", user="saread", password='sa123', database="qbdb")
    engine_103 = create_engine('mssql+pyodbc://sa:sa123@192.168.87.103:1433/data_reg?driver=SQL+Server')
    conn_103 = pymssql.connect(host='192.168.87.103', user='sa', password='sa123', database='data_reg')

    #
    # 表字段 createDate
    columns = ['createDateTime', 'bid', 'ofr', 'last_bid', 'last_ofr', 'bondCode', 'bid_cleanprice',
               'ofr_cleanprice', 'last_bid_cleanprice', 'last_ofr_cleanprice', 'trdyield', 'last_trdyield',
               'trd_cleanprice', 'last_trd_cleanprice']
    #
    # 入库债券
    bond_pool = ('180013.IB','180023.IB','180016.IB','180015.IB','180214.IB','180204.IB','170215.IB','170210.IB',
         '180011.IB','180209.IB', '180208.IB', '180211.IB', '180210.IB', '180206.IB', '180212.IB' ,
        	'180304.IB','180309.IB','180313.IB','180406.IB','180010.IB','180019.IB','180205.IB','190205.IB',
                 '190210.IB')

    # bond_pool = ('180205.IB')

    def data_sample(self, df1, code, dataDicts):
        def f(row, col, dataDicts, conn=self.conn_43):
            bondcalc = BondCalc(row.bondCode)
            bondcalc.getBondInfo(conn, dataDicts)
            bondcalc.parseBondInfo()
            pv, cleanprice, accrued_interest = bondcalc.PVandCleanPrice_calc(row.createDateTime, row[col])
            return cleanprice

        df_bid = df1.bid.resample('1s').min().rename('bid', inplace=True)
        df_ofr = df1.ofr.resample('1s').max().rename('ofr', inplace=True)
        df_trdyield = df1.latestTradePrice.resample('1s').last().rename('trdyield', inplace=True)
        df2 = pd.concat([df_bid, df_ofr, df_trdyield], axis=1)
        Datestr = df2.index[0].strftime("%Y-%m-%d")
        ##################################################
        temp_bid = df2[(df2.index < Datestr + ' 09:00:00') & (df2.bid.notnull())].bid.sort_index()
        bid0 = temp_bid[-1] if len(temp_bid) > 0 else np.nan
        temp_ofr = df2[(df2.index < Datestr + ' 09:00:00') & (df2.ofr.notnull())].ofr.sort_index()
        ofr0 = temp_ofr[-1] if len(temp_ofr) > 0 else np.nan
        temp_trdyield = df2[(df2.index < Datestr + ' 09:00:00') & (df2.trdyield.notnull())].trdyield.sort_index()
        trdyield0 = temp_trdyield[-1] if len(temp_trdyield) > 0 else np.nan
        ##################################################

        bondcalc = BondCalc(code)
        bondcalc.getBondInfo(self.conn_43, dataDicts)
        bondcalc.parseBondInfo()
        bid0_cleanprice = bondcalc.PVandCleanPrice_calc(Datestr, bid0)[1] if not np.isnan(bid0) else np.nan
        ofr0_cleanprice = bondcalc.PVandCleanPrice_calc(Datestr, ofr0)[1] if not np.isnan(ofr0) else np.nan
        trdyield0_cleanprice = bondcalc.PVandCleanPrice_calc(Datestr, trdyield0)[1] if not np.isnan(
            trdyield0) else np.nan

        # 将时间对齐到指定的网格
        DateIndex = pd.date_range(start=Datestr + " 09:00:01", end=Datestr + " 16:30:00", freq='s')
        df2 = df2.reindex(DateIndex)
        ######################################
        # 更新index标签，并整合至数据框
        df2.index.name = 'createDateTime'  #
        df2.reset_index(inplace=True)
        # 更新bondCode, last_bid, last_ofr, bid_cleanprice, ofr_cleanprice
        df2['bondCode'] = code
        df2['last_bid'] = df2.bid.fillna(method='ffill').fillna(bid0)
        df2['last_ofr'] = df2.ofr.fillna(method='ffill').fillna(ofr0)
        df2['last_trdyield'] = df2.trdyield.fillna(method='ffill').fillna(trdyield0)
        df2['bid_cleanprice'] = df2[df2.bid.notnull()].apply(lambda row: f(row, 'bid', dataDicts), axis=1) if len(
            df2[df2.bid.notnull()]) > 0 else np.nan
        df2['ofr_cleanprice'] = df2[df2.ofr.notnull()].apply(lambda row: f(row, 'ofr', dataDicts), axis=1) if len(
            df2[df2.ofr.notnull()]) > 0 else np.nan
        df2['trd_cleanprice'] = df2[df2.trdyield.notnull()].apply(lambda row: f(row, 'trdyield', dataDicts),
                                                                  axis=1) if len(
            df2[df2.trdyield.notnull()]) > 0 else np.nan
        df2[['last_bid_cleanprice', 'last_ofr_cleanprice', 'last_trd_cleanprice']] = df2[
            ['bid_cleanprice', 'ofr_cleanprice', 'trd_cleanprice']].fillna(method='ffill')
        # 将数据框头部补齐
        df2.last_bid_cleanprice.fillna(bid0_cleanprice, inplace=True)
        df2.last_ofr_cleanprice.fillna(ofr0_cleanprice, inplace=True)
        df2.last_trd_cleanprice.fillna(trdyield0_cleanprice, inplace=True)

        # 存储数据库
        df2.to_sql(name="QBBBO_history_reg1", con=self.engine_103, index=False, if_exists='append', chunksize=4000)

        # 更新数据库
        #    cursor = conn_103.cursor()
        #    df2.apply(lambda row: update2qb(row.trdyield, row.last_trdyield, row.trd_cleanprice, row.last_trd_cleanprice,
        #                                        row.bondCode, row.createDateTime,cursor), axis=1)
        #
        print(code + "已入库")

        return df2

    # 一天内的最优报价及计算的净价
    def singleTask(self, start_time, end_time, conn, dataDicts=dict(), database='QBBBOVIEW'):
        sql = """
        SELECT
            *
        FROM
            dbo."""+database+"""
        WHERE
            dbo."""+database+""".createDateTime between '%s 06:00:01' and '%s 16:30:00' AND
            dbo."""%(start_time.strftime('%Y-%m-%d'), start_time.strftime('%Y-%m-%d'))+database+""".bondCode in %s 
        """ % str(self.bond_pool)

        df = pd.read_sql(sql, con=self.conn_43, index_col='createDateTime')
        if df is not None and (df.shape[0] > 0):
            df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")
            df['bid'] = df.bid.apply(self.str2float)
            df['ofr'] = df.ofr.apply(self.str2float)
            df['latestTradePrice'] = df.latestTradePrice.apply(self.str2float)
            for code in df.bondCode.unique():
                self.data_sample(df[df.bondCode == code], code, dataDicts)
            return df
        else:
            return None

    #########################################################
    # 判断一个字符是否是可float化
    #########################################################
    def is_eff_number(self, s):
        if type(s) is str:
            s_list = s.strip().split('.')
            if len(s_list) == 2 and s_list[0].isdigit() and s_list[1].isdigit():
                return True
            else:
                return False
        else:
            return False

    def str2float(self, s):
        if self.is_eff_number(s):
            return float(s)
        else:
            return np.nan

    def routine_task(self, start_time, end_time, dataDicts=dict()):
        # if type(start_time) is str:
        #     start_time = pd.to_datetime(start_time)
        # if type(end_time) is str:
        #     end_time = pd.to_datetime(end_time)
        date_range = pd.date_range(start=start_time, end=end_time, freq='d')
        for start_time, end_time in zip(date_range[:-1], date_range[1:]):
            output = self.singleTask(start_time, end_time, self.conn_43, dataDicts)
            print(start_time.strftime("%Y-%m-%d") + "数据已入库")

    def update2qb(self, df, bondCode):
        cursor = self.conn_103.cursor()
        df1 = df[df.bondCode == "bond"]
        df1.sort_values(by='createDateTime', inplace=True)
        df1[df1.last_trdyield > 90][['last_trdyield', 'last_trd_cleanprice']] = np.nan
        df1[['last_trdyield', 'last_trd_cleanprice']].fillna(method='ffill', inplace=True)

        def f(last_trdyield, last_trd_cleanprice, createDateTime, bondCode):
            sql = """
                UPDATE
                QBBBO_history_reg1 SET trdyield = null , last_trdyield = '%s' , trd_cleanprice = null , last_trd_cleanprice = "%s"
                WHERE createDateTime = '%s' and bondCode = '%s'
                """ % (last_trdyield, last_trd_cleanprice, createDateTime, bondCode)
            try:
                cursor.execute(sql)
                conn_103.commit()
            except:
                conn_103.rollback()

        df1[df1.last_trdyield > 90].apply(
            lambda row: f(row.last_trdyield, row.last_trd_cleanprice, row.createDateTime, row.bondCode))
        cursor.close()

    def ex_update2qb(start_time, end_time):
        pd.date_range(start_time, end_time, freq="d")
        date_range = fetch_localhost_data()
        for start_time, end_time in zip(date_range[:-1], date_range[1:]):
            df = fetch_localhost_data(start_time, end_time, conn_103)
            for bond in bond_pool:
                update2qb(df[df.bondCode == bond], bond)
            print(start_time.strftime("%Y-%m-%d") + "已更新")

    def fetch_localhost_data(start_time, end_time, conn):
        sql = """
            SELECT
                *
            FROM
                dbo.QBBBO_history
            WHERE
                dbo.QBBBO_history.createDateTime between '%s' and '%s' AND
                dbo.QBBBO_history.bondCode in %s
            """ % (start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d'), str(bond_pool))
        df = pd.read_sql(sql, conn)
        return df

if __name__ == '__main__':
    dataDicts = dict()
    # routine_task('2018-08-01', '2018-11-14', dataDicts)
    dbdata = QBdata()
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(1)
    tomorrow = now + datetime.timedelta(1)
    dbdata.routine_task(now.strftime("%Y-%m-%d 00:00:00"), tomorrow.strftime("%Y-%m-%d 00:00:00"), dataDicts)

# dbdata.routine_task(yesterday.strftime("%Y-%m-%d 00:00:00"), now.strftime("%Y-%m-%d 00:00:00"), dataDicts)
# routineTask('20181102','20181103',dataDicts)


# '''DELETE
# FROM
# 	QBBBO_history_reg1
# WHERE
# 	id IN (
# 		SELECT
# 			MIN (id)
# 		FROM
# 			QBBBO_history_reg1
# 		WHERE
# 			createDateTime > '2018-09-18'
# 		AND createDateTime <= '2018-09-19'
# 		GROUP BY
# 			bondCode,
# 			createDateTime
# 	)'''

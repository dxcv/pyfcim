# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 14:05:50 2018

@author: l_cry
"""
import pandas as pd
import pymssql
from datetime import datetime, timedelta

#conn = pymssql.connect(host = "10.28.7.43",user = "saread",password = 'sa123',database = "qbdb")
class BondCalc:

    # 类型：
    # 1 到期一次还本付息 
    # 2 到期按面值偿还
    # 3 每年。。。付息
    
    # BondCalc类初始化
    def __init__(self, bondCode):
        self.bondCode = bondCode

    def __repr__(self):
        if self.bond_info:
            print(self.bond_info)
        else:
            print(self.bondCode)
    
    def parseBondInfo(self):
        if self.bond_info:
            (BondCode,self.BondName,Couponrate,Frequency,CarryDate,EndDate,MaturityDate,TermYear,CouponTxt)=self.bond_info
        if type(CarryDate) is str:
            self.CarryDate = pd.to_datetime(CarryDate)
        if type(EndDate) is str:
            self.EndDate = pd.to_datetime(EndDate)
        if type(MaturityDate) is str:
            self.MaturityDate = pd.to_datetime(MaturityDate)
        self.coupon_type,self.date_notes = self.parse_CouponDate(CouponTxt)
        self.Frequency = self.__parse_Frequency(Frequency)
        self.TermYear = float(TermYear)
        if self.coupon_type == 3 or self.coupon_type == 1:
            self.Couponrate = float(Couponrate)
        elif self.coupon_type == 2:
            self.Couponrate = 0
        return self.bond_info
        
    
    def getBondInfo(self,conn,dataDicts=dict()):
        if self.bondCode in dataDicts.keys():
            self.bond_info = dataDicts[self.bondCode]
            return self.bond_info, dataDicts
        else:
            sql_wind = """
            SELECT
            	*
            FROM
            	OPENQUERY (
            		WINDNEW,
            		'select S_INFO_WINDCODE,B_INFO_FULLNAME,B_INFO_COUPONRATE,B_INFO_INTERESTFREQUENCY,
                    B_INFO_CARRYDATE,B_INFO_ENDDATE,B_INFO_MATURITYDATE,B_INFO_TERM_YEAR_,B_INFO_COUPONDATETXT
             from CBondDescription where S_INFO_WINDCODE = ''%s'''
            	)
            """% self.bondCode
            cur=conn.cursor()
            cur.execute(sql_wind)
            self.bond_info = cur.fetchone()   
            dataDicts[self.bondCode] = self.bond_info # 将查询到的数据存储到本地
            cur.close()
        return self.bond_info, dataDicts
    """
        (BondCode,BondName,Couponrate,Frequency,CarryDate,EndDate,MaturityDate,TermYear,CouponTxt)=bond_info
    """
    
    # 付息日期解析
    def parse_CouponDate(self, text):
        if "到期按面值偿还" in text:
            coupon_type = 2
            return coupon_type,None
        elif "到期一次还本付息" in text:
            coupon_type = 1
            return coupon_type,None
        else:
            coupon_type = 3
            text = text.strip().replace(",节假日顺延",'').replace("每年","").replace("付息","").replace("和",",")
            text = text.split(",")
            date_notes = []
            for datestr in text:
                if '月' in datestr:
                    date_notes.append(list(map(int,datestr.replace("月","-").replace("日","").split("-"))))
                else:  #0118这样的格式
                    date_notes.append([int(datestr[0:2]),int(datestr[2:4])])
            date_notes.sort()
            return coupon_type,date_notes
        
    
    # 返回到期剩余期数 和 付息日期 下一次付息日期
    def parse_NextCashFlowDay(self,Date):
        if type(Date) is str:
            Date = pd.to_datetime(Date)
#        if type(self.MaturityDate) is str:
#            self.MaturityDate = pd.to_datetime(self.MaturityDate)
        CashFlowDayList=[]
        if self.coupon_type==3:
            for year in range(Date.year,self.MaturityDate.year+1):
                for item in self.date_notes:
                    new_Date = datetime(year,item[0],item[1])
                    if new_Date >= Date and new_Date <= self.MaturityDate:
                        CashFlowDayList.append(new_Date)
            remain_num=len(CashFlowDayList)
            return remain_num, CashFlowDayList, CashFlowDayList[0]
        elif self.coupon_type==1 or self.coupon_type==2:
            if Date < self.MaturityDate:
                remain_num = 1
                CashFlowDayList.append(self.MaturityDate)
                return remain_num, CashFlowDayList, CashFlowDayList[0]
            else:
                "已过债券存续期"
        else:
            pass
            
            
    
    # 返回上一次付息时间
    def parse_lastCashFlowDay(self, Date):
        if type(Date) is str:
            Date = pd.to_datetime(Date)
        if Date < self.CarryDate:
            return "日期在存续期之前"
        if self.coupon_type==3:
            for year in range(Date.year,self.CarryDate.year-1,-1):
                new_DateList = []
                for item in self.date_notes:
                    new_Date = datetime(year,item[0],item[1])
                    if new_Date < Date:
                        new_DateList.append(new_Date)
                if len(new_DateList)>0:
                    return max(new_DateList)
        elif self.coupon_type==1 or self.coupon_type==2:
            return self.CarryDate
        else:
            pass
        
    # 解析下一次付息剩余 和 本次付息周期
    def parse_DandTSandN(self, Date):
        if type(Date) is str:
            Date = pd.to_datetime(Date)
        remain_num, CashFlowDayList, NextDate = self.parse_NextCashFlowDay(Date)
        LastDate = self.parse_lastCashFlowDay(Date)
        d = NextDate - Date
        TS = NextDate - LastDate
        return d, TS, remain_num
    
    
    # 判断日期是否为节假日
    def isweekend(self, Date):
        if type(Date) is str:
            Date = pd.to_datetime(Date)
        if 6 > Date.weekday() > 0:
            return 0
        else:
            return 1
    
    
    # 解析付息频率
    def __parse_Frequency(self, freq):
        if freq:
            if freq[0] == 'Y':
                return 1/int(freq[1])
            elif freq[0] == 'M':
                return 12/int(freq[1])
            else:
                return 0
        else:
            return None
    
    def is04year(self, Date):
        if type(Date) is str:
            Date = pd.to_datetime(Date)
        year = Date.year
        if year%4==0 and year%400 !=0:
            return True
        else:
            return False
    
    
    # 计算全价 c_r每期利息，d下期付息天数剩余，TS本期付息周期，f付息频率，r到期收益率
    def PVandCleanPrice_calc(self,Date,r):
        if type(Date) is str:
            Date = pd.to_datetime(Date)
        r = r/100
        d, TS, n = self.parse_DandTSandN(Date)
        c_r = self.Couponrate
        w = d/TS
        if self.coupon_type==3:
            f = self.Frequency
            pv = 0
            for i in range(n-1):
                pv += c_r/f/(1+r/f)**(w+i)
            pv += (c_r/f+100)/(1+r/f)**(w+n-1)
            accrued_interest = (TS-d)/TS*self.Couponrate/self.Frequency
            return pv, pv-accrued_interest,accrued_interest
        elif self.coupon_type==1:
            if self.TermYear<=1:
                pv = (100+self.Couponrate)/(1+d/timedelta(365)*r) #待修正
                accrued_interest = (1-w)*TS/timedelta(365)*self.Couponrate
                return pv, pv-accrued_interest,accrued_interest
            else:
                pass # 按复利处理
        elif self.coupon_type==2:
            if self.TermYear <= 1:
                pv = (100+self.Couponrate)/(1+d/timedelta(365)*r) #待修正
                accrued_interest = 0
            return pv, pv-accrued_interest,accrued_interest
    
    
    # 计算应计利息
    def accrued_interest_calc(self,Date):
        if type(Date) is str:
            Date = pd.to_datetime(Date)
        d, TS, n = self.parse_DandTSandN(Date)
        return (TS-d)/TS*self.Couponrate/self.Frequency
    
    
    # 计算净价
    def clean_price_calc(self,d,TS,n,r):
        pv = self.pv_calc(self,d,TS,n,r)
        accrued_interest = self.accrued_interest_calc(d,TS)
        return pv - accrued_interest


#class DataStore:
#    DataSet=set()
#    def insert(item):
#        if type()
#    
    
    
    
    
#def price_cal(bondCode,Date,r,con=conn):
#    (BondCode,BondName,Couponrate,Frequency,CarryDate,EndDate,MaturityDate,TermYear,CouponTxt)=CBondInfo(bondCode,con)
#    cleanPrice, pv = _price_calc(Date,r,BondCode,BondName,Couponrate,Frequency,CarryDate,EndDate,MaturityDate,TermYear)
#    return cleanPrice, pv
#net_price = data_extract('2018-10-26',0.03,BondCode,BondName,Couponrate,Frequency,CarryDate,EndDate,MaturityDate,TermYear)

if __name__ == '__main__':
    conn = pymssql.connect(host="10.28.7.43", user="saread", password='sa123', database="qbdb")
    dataDicts = dict()
    bondcalc = BondCalc('180024.IB')
    bondcalc.getBondInfo(conn,dataDicts)
    bondcalc.parseBondInfo()
    pv, cp, accrued_interest = bondcalc.PVandCleanPrice_calc('20190212',3.75)

    codes=['180024.IB','180017.IB','180006.IB','170022.IB','170015.IB','170005.IB','160019.IB','160008.IB']
    re = []
    for code in codes:
        bondcalc = BondCalc(code)
        bondcalc.getBondInfo(conn,dataDicts)
        bondcalc.parseBondInfo()
        pv, cp, accrued_interest = bondcalc.PVandCleanPrice_calc('20190212', 3.75)
        re.append([code, pv, cp, accrued_interest])


    df = pd.DataFrame(re,columns=('code','全价','净价','应计利息'))
    print("over")






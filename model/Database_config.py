
import pymssql
from sqlalchemy import create_engine





# 数据库配置
conn_43 = pymssql.connect(host = "10.28.7.43",user = "saread",password = 'sa123',database = "qbdb")
conn_43_creditdb = pymssql.connect(host = "10.28.7.43",user = "sa",password = 'tcl+nftx',database = "creditdb")
engine_103 = create_engine('mssql+pyodbc://sa:sa123@192.168.87.103:1433/data_reg?driver=SQL+Server')

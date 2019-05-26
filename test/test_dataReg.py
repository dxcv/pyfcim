from unittest import TestCase
from model import DataReg
from model.Database_config import engine_103
import pandas as pd

class TestDataReg(TestCase):
    def test_is_outlier(self):
        self.fail()

    def test_keras_model(self):
        self.fail()

    def test_y_reg(self):
        self.fail()

    def test_qb_reg(self):
        sql = """select * from dbo.QBBBO_history_reg where bondCode='180205.IB' and createDateTime>'2018-09-03 16:00:00'
                                       and createDateTime<='2018-09-10 16:30:00' order by createDateTime
                                       """
        df = pd.read_sql_query(sql, engine_103)
        datareg = DataReg()
        df1 = datareg.qb_reg(df)
        # self.fail()

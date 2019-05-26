from unittest import TestCase
from model.BondCalc import BondCalc


bondcalc = BondCalc('180004.IB')


class TestBondCalc(TestCase):
    def test_parseBondInfo(self):
        self.fail()

    def test_getBondInfo(self):
        self.fail()

    def test_parse_NextCashFlowDay(self):
        self.fail()

    def test_parse_lastCashFlowDay(self):
        self.fail()

    def test_parse_DandTSandN(self):
        self.fail()

    def test_isweekend(self):
        self.fail()

    def test_is04year(self):
        bool = bondcalc.is04year("20181103")
        self.assertEqual(False, bool)

    def test_PVandCleanPrice_calc(self):
        self.fail()

    def test_accrued_interest_calc(self):
        self.fail()

    def test_clean_price_calc(self):
        self.fail()

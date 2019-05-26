from unittest import TestCase
from model.CrawlerSHC import CrawlerSHC

class TestCrawlerSHC(TestCase):
    def test_crawbyDate(self):
        crawshc = CrawlerSHC()
        crawshc.crawbyDate('20181120')

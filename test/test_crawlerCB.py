from unittest import TestCase
from model.CrawlerCB import CrawlerCB


class TestCrawlerCB(TestCase):
    def test_crawbyDate(self):
        crawlercb = CrawlerCB()
        crawlercb.crawbyDate("2018-11-19")
        # crawlercb.crawbyDate("2018-11-14")
        # crawlercb.crawbyDate("2018-11-08")
        # crawlercb.crawbyDate("2018-11-09")
        # crawlercb.crawbyDate("2018-11-13")


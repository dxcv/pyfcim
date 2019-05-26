import sys
sys.path.append("../")
import multiprocessing
from model.CrawlerSHC import CrawlerSHC
from model.CrawlerCB import CrawlerCB
from datetime import datetime, timedelta

crawlershc = CrawlerSHC()
crawlercb = CrawlerCB()

now = datetime.now() - timedelta(2)
yesterday = now - timedelta(1)
tomorrow = now + timedelta(1)

if __name__ == '__main__':
    try:
        crawlershc.crawbyDate(now.strftime("%Y-%m-%d"))
    except:
        print("上清所爬取失败")

    try:
        crawlercb.crawbyDate(now.strftime("%Y-%m-%d"))
    except:
        print("中债登爬取失败")







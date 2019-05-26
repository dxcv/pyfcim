import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import pandas as pd
import os
import requests
from retry import retry
from lxml import etree


class CrawlerSHC:

    post_headers = {
        "Host": "www.shclearing.com",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Origin": "http://www.shclearing.com",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        # "Referer": "http://www.shclearing.com/xxpl/fxpl/mtn/201811/t20181116_451191.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",

    }
    urls = {
        "mtn": "http://www.shclearing.com/xxpl/fxpl/mtn",
        "cp": "http://www.shclearing.com/xxpl/fxpl/cp",
        "scp": "http://www.shclearing.com/xxpl/fxpl/scp"
    }

    link = "http://www.shclearing.com/xxpl/fxpl/"
    db_path = "C:/Users/l_cry/Desktop/docs/"
    # db_path = "ftp://192.168.87.103/docs/"

    def __init__(self):
        options = Options()
        # options.add_argument('-headless')
        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(30)
        self.timewait = 15

    ########################################################################
    # 根据日期抓取信息
    def crawbyDate(self, Date):
        if type(Date) is str:
            Date = pd.to_datetime(Date)

        for type_en in self.urls.keys():
            time.sleep(6)
            url = self.urls[type_en]
            for i in range(100):
                status=1 # 标记循环状态
                r = requests.get(
                    url,
                    headers=self.post_headers
                )
                if r.status_code == 200:
                    page = etree.HTML(r.text)
                    bonds = page.xpath("//div[@class='fk_wrapper']/div[@class='r_con']/ul[@class='list']/li")
                    for bond in bonds:
                        if self.__parse_bond(bond, type_en, Date) == 0:
                            status = 0
                            break
                    if status == 0:
                        break # 结束外循环状态
                    else: url = url + "/index_%s.html"% str(i+1)
        self.browser.close()



    @retry(tries=3, delay=10)
    def __parse_bond(self, bond, type_name, Date, sub_name=None):
        if sub_name is None:
            dir_path = self.db_path + type_name
        else:
            dir_path = self.db_path + type_name + "/" + sub_name
        href = self.urls[type_name]+bond.xpath("a/@href")[0][1:]
        timestr = bond.xpath("span/text()")[0]
        timetime = datetime.strptime(timestr, "%Y-%m-%d")  # 当前公告发布日期时间
        file_notes = {}
        if timetime < Date:
            return 0 # 更改循环状态
        if timetime == Date:
            res = requests.get(
                href,
                headers=self.post_headers
            )
            if res.status_code != 200:
                raise Exception("http error")
            if 'text/html' in res.headers['Content-Type']:
                self.browser.get(href)
                content = self.browser.find_element_by_id("title").text.replace('（', '(').replace('）', ')')
                files = self.browser.find_elements_by_xpath("//div[@id='content']/div[@class='attachments']/a")
                for file in files:
                    file_info = file.get_attribute("href").replace("javascript:download", "").split("'")
                    file_code = file_info[1].replace("./", "")
                    file_name = file_info[3]
                    if self.isdownload(type_name, file.text):
                        data = {
                            "FileName": file_code,
                            "DownName": file_name
                        }

                        r = requests.post('http://www.shclearing.com/wcm/shch/pages/client/download/download.jsp', data=data, headers=self.post_headers)
                        if r.status_code == 200:
                            file_path = dir_path + "/" + timestr + "/" + content
                            if not os.path.exists(file_path):
                                os.makedirs(file_path)

                            with open(file_path + "/" + file.text, "wb") as code:
                                code.write(r.content)

                            file_notes[content] = file_path
        return file_notes

    # 判断文件是否需要下载
    @staticmethod
    def isdownload(type_name, file_title):
        if type_name in ("mtn"):
            if (file_title.find("募集说明书") != -1 and file_title.find("募集说明书摘要") == -1) or file_title.find('评级报告') != -1:
                return True
            else:
                return False
        elif type_name in ("cp"):
            if (file_title.find("募集说明书") != -1 and file_title.find("募集说明书摘要") == -1) or file_title.find('评级报告') != -1:
                return True
            else:
                return False
        elif type_name in ("scp"):
            if (file_title.find("募集说明书") != -1 and file_title.find("募集说明书摘要") == -1) or file_title.find('评级报告') != -1:
                return True
            else:
                return False
        else:
            return False



    # def change_name(self, bond_name):

if __name__ == '__main__':
    crawlershc = CrawlerSHC()
    now = datetime.now()
    yesterday = now - timedelta(1)
    tomorrow = now + timedelta(1)
    try:
        crawlershc.crawbyDate(now.strftime("%Y-%m-%d"))
    except:
        print("上清所爬取失败")






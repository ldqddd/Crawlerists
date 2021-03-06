
from scrapy import signals
import pymysql
from itemadapter import is_item, ItemAdapter
from scrapy.http import Request, Response
from fake_useragent import UserAgent
from scrapy.exceptions import IgnoreRequest

header = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
}

class DemoSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s


        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider): 
        for i in result:
            if isinstance(i,Request):
                yield i
            else:
                i['html'] = response.text
                i['request_url'] = response.request.url
                i['response_url'] = response.url
                i['website_id'] = spider.website_id
                i['language_id'] = spider.language_id
                if 'images' not in i:
                    i['images'] = []
                yield i

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        

class DemoDownloaderMiddleware:
    def __init__(self):
        self.db = None
        self.cur = None      
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider): 
        self.cur.execute('select request_url from news where request_url = %s',request.url)
        result = self.cur.fetchall()

        if result == ():
            header['User-Agent'] = header['User-Agent']
            request = Request(request.url,headers=header,meta=request.meta)
            return None
        else:
            spider.logger.info('filtered url')
            return IgnoreRequest

    def spider_opened(self, spider): 
        self.db = pymysql.connect(
            host=spider.sql['host'],
            user=spider.sql['user'],
            password=spider.sql['password'],
            db=spider.sql['db'],
        )
        self.cur = self.db.cursor()
        
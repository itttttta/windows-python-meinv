#!/usr/bin/python
#-*-coding:utf-8-*-
import scrapy
import time

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request

from meinv.items import MeinvItem
import urlparse
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError


class Spider(scrapy.Spider):
    name = "ninetwo_spider"
    start_urls = ['http://m.92mntu.com']
    handle_httpstatus_list = [301, 302]

    # scrapy.Request.custom_settings =

    #抓取列表处理
    def parse(self, response ):
        print 'parsing ', response.url
        sel = Selector(response)
        meinvs = sel.xpath('//div[@class="post"]')
        # meinv = meinvs[0]
        # item = self.load_item(meinv)
        # yield Request(item['url'], meta={'item': item}, callback=self.parse_item,dont_filter=True,errback=self.errback_httpbin)
        for index,d in enumerate(meinvs):
            item = self.load_item(d)
            yield item
            # yield Request(item['url'], meta={'item': item}, callback=self.parse_item, dont_filter=True,
            #               errback=self.errback_httpbin)

    #模型处理
    def load_item(self, d):
        item = MeinvItem();
        item['title'] = d.css('a::attr(title)').extract_first()
        item['url'] =  'http://m.92mntu.com'+d.css('a::attr(href)').extract_first()
        item['img'] = d.css('img::attr(src)').extract_first()
        item['img'] = item['img'].replace('www.','')
        item['img_arrs'] = []
        item['url_arrs'] = []
        item['catalogue'] = self.catalogue(item['url'])
        item['create_time'] = time.time()
        print d.css('a::attr(title)').extract_first()
        return item


    #内容详情 所有图片
    def parse_item(self, response):
        item = response.meta['item']
        sel = Selector(response)
        img = sel.xpath('//div[@class="arpic"]/ul/li/a/img/@src').extract()
        urls = sel.xpath('//div[@class="arfy"]/ul/li/a/@href').extract()
        if len(item['img_arrs']):
            item['img_arrs'].append(img.pop())
        else:
            item['img_arrs'] = img
        if len(urls) ==2:
            baseUrl =''
            if len(item['url_arrs']):
                baseUrl = urlparse.urljoin(response.url, urls[1])
                if baseUrl == response.url:
                    yield item
                item['url_arrs'].append(baseUrl)
            else:
                baseUrl = urlparse.urljoin(response.url,urls[1])
                if baseUrl== response.url:
                    yield item
                item['url_arrs'] = [baseUrl]
            #判断是否最后一个img 如果不是 继续添加url
            if(item['url_arrs'][-1]!= response.url):
                yield Request(item['url_arrs'][-1], meta={'item': item}, callback=self.parse_item, dont_filter=True,
                              errback=self.errback_httpbin)
        else:
            yield item

    #错误处理
    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            # you can get the response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    #根据url 分类
    def catalogue(self,url):
        catalogue = '美女'
        if(url.find('rhmn')):
            catalogue = '日韩美女'
        elif(url.find('xgmn')):
            catalogue = '性感美女'
        elif (url.find('swmn')):
            catalogue = '丝袜美女'
        elif (url.find('mncm')):
            catalogue = '美女车模'
        elif (url.find('mnmx')):
            catalogue = '美女明星'
        return catalogue
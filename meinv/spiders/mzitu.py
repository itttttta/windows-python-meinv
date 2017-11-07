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
    name = "mzitu_spider"
    start_urls = ['http://www.mzitu.com/']
    handle_httpstatus_list = [301, 302]

    # scrapy.Request.custom_settings =

    #抓取列表处理
    def parse(self, response ):
        print 'parsing ', response.url
        sel = Selector(response)
        meinvs = sel.xpath('//div[@class="postlist"]/ul/li/a/@href').extract()
        helpUrls = sel.xpath('//a[@class="page-numbers"]/@href').extract()
        # meinv = meinvs[0]
        # item = self.load_item(meinv)
        # yield Request(item['url'], meta={'item': item}, callback=self.parse_item,dont_filter=True,errback=self.errback_httpbin)
        for index,d in enumerate(meinvs):
            yield Request(d, callback=self.parse_item, dont_filter=False, errback=self.errback_httpbin)
        for index, url in enumerate(helpUrls):
            # print 'helpUrl = ' + url
            yield Request(url, callback=self.parse, dont_filter=False, errback=self.errback_httpbin)



    #模型处理
    def parse_item(self, response):
        sel = Selector(response)
        item = MeinvItem()

        if response.meta.has_key('item') == False:
            item['url'] = response.url
            item['title'] = sel.xpath('//h2[@class="main-title"]/text()').extract_first()
            item['img'] = sel.xpath('//div[@class="main-image"]/p/a/img/@src').extract_first()
            item['img_arrs'] = []
            item['catalogue'] = sel.xpath('//a[@rel="category tag"]/text()').extract_first()
        else:
            item = response.meta['item']

        item['img_arrs'].append({
            'img_title': sel.xpath('//h2[@class="main-title"]/text()').extract_first(),
            'img_url': sel.xpath('//div[@class="main-image"]/p/a/img/@src').extract_first()
        })
        item['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item['origin_time'] = sel.xpath('//span[contains(text(), "-")]').extract_first()

        next_page = sel.xpath('//div[@class="main-image"]/p/a/@href').extract_first()
        if next_page.find(item['url']) != -1:
            yield Request(next_page, meta={'item': item}, callback=self.parse_item, dont_filter=False, errback=self.errback_httpbin )
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
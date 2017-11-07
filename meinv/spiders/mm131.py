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
from datetime import  datetime
global base_url
base_url = 'http://www.mm131.com/'

class Spider(scrapy.Spider):
    name = "mm131_spider"
    start_urls = ['http://www.mm131.com/']

    handle_httpstatus_list = [301, 302]

    # scrapy.Request.custom_settings =

    #抓取列表处理
    def parse(self, response ):
        print 'parsing ', response.url
        # print response.body
        sel = Selector(response)
        meinvs = sel.xpath('//div[@class="main"]/dl/dd')
        hrefs = sel.xpath('//a/@href').extract()
        content_pic = sel.xpath('//div[@class="content-pic"]').extract()
        # meinv = meinvs[0]
        # item = self.load_item(meinv)

        for index ,href in enumerate(hrefs):
            if(href.find(base_url)!=-1 and href.find('.html')!=-1):
                print 'href = ' + href
                yield Request(href, callback=self.parse,dont_filter=True,errback=self.errback_httpbin)

        if(len(content_pic)):
            print 'pic = '+content_pic[0];
            item =  self.load_item(response)
            yield item
        # for index,d in enumerate(meinvs):
        #     print d
        #     item = self.load_item(d)
        #     # yield item
        #     yield Request(item['url'], meta={'item': item}, callback=self.parse_item, dont_filter=True,
        #                   errback=self.errback_httpbin)

    #模型处理
    def load_item(self, response):
        item = MeinvItem();
        sel = Selector(response)
        item['title'] = sel.xpath('//div[@class="content"]/h5/text()').extract()[0]
        item['img'] = sel.xpath('//div[@class="content-pic"]/a/img/@src').extract()[0]
        item['origin_time'] = sel.xpath('//div[@class="content-msg"]/text()').extract()[0][5:]
        # item['origin_time'] = datetime.strptime(item['origin_time'], "%Y-%m-%d %H:%M%S")
        # dt_string = '2011-07-15 13:00:00+00:00'
        # new_dt = dt_string[:19]
        # dt = datetime.strptime(new_dt, '%Y-%m-%d %H:%M:%S')
        item['url'] = response.url;
        item['url_arrs'] = [item['url']]
        item['img_arrs'] = [item['img']]
        item['catalogue'] = self.catalogue(item['url'])
        item['create_time'] = datetime.now()
        item['is_show'] = True
        count = sel.xpath('//div[@class="content-page"]/span[@class="page-ch"]/text()').extract()[0]
        count = int(count[1:-1])
        for num in range(2, count):
            item['url_arrs'].append(response.url[0:-5] + '_' + str(num) + '.html')
            item['img_arrs'].append(item['img'][0:-5] + str(num) + '.jpg')
            print(item)
        return item


    #内容详情 所有图片
    def parse_item(self, response):

        item = MeinvItem();
        sel = Selector(response)
        item['title'] = sel.xpath('//div[@class="content"]/h5/text()').extract()[0]
        item['img'] = sel.xpath('//div[@class="content-pic"]/a/img/@src').extract()[0]
        item['origin_time'] =  sel.xpath('//div[@class="content-msg"]/text()').extract()[0][5:]
        # item['origin_time'] = datetime.strptime(item['origin_time'], "%Y-%m-%d %H:%M%S")
        # dt_string = '2011-07-15 13:00:00+00:00'
        # new_dt = dt_string[:19]
        # dt = datetime.strptime(new_dt, '%Y-%m-%d %H:%M:%S')
        item['url'] = response.url;
        item['url_arrs'] = [item['url']]
        item['img_arrs'] = [item['img']]
        item['catalogue'] = self.catalogue(item['url'])
        item['create_time'] = datetime.now()
        item['is_show'] = True
        count = sel.xpath('//div[@class="content-page"]/span[@class="page-ch"]/text()').extract()[0]
        count = int(count[1:-1])
        for num in range(2,count):
            item['url_arrs'].append(response.url[0:-5]+'_'+str(num)+'.html')
            item['img_arrs'].append(item['img'][0:-5]+str(num)+'.jpg')
            print(item)
        return item


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
        if(url.find('qingchun')):
            catalogue = '清纯美女'
        elif(url.find('xinggan')):
            catalogue = '性感美女'
        elif (url.find('xiaohua')):
            catalogue = '美女校花'
        elif (url.find('chemo')):
            catalogue = '性感车模'
        elif (url.find('qipao')):
            catalogue = '旗袍美女'
        return catalogue
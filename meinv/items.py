# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MeinvItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    type = scrapy.Field()
    base_url = scrapy.Field()
    catalogue =  scrapy.Field()
    create_time = scrapy.Field()
    origin_time = scrapy.Field()
    img = scrapy.Field()
    img_arrs = scrapy.Field()
    url = scrapy.Field()
    url_arrs = scrapy.Field()
    up_count = scrapy.Field()
    down_count = scrapy.Field()
    watch_count = scrapy.Field()
    comment_count = scrapy.Field()
    image_paths = scrapy.Field()
    is_show = scrapy.Field()
    pass

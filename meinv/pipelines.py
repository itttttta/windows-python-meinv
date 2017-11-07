# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from items import MeinvItem
from meinv.Dao.mongodb import mongodb
class MeinvPipeline(object):
    def process_item(self, item, spider):
        mongodb().insert(item)
        return item

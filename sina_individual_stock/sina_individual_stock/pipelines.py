#-*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sina_individual_stock.spiders.individual_stock import SinaStockSpider

from avrotools.avro_utils import AvroUtils
from common.config import kafka_producer
from time import sleep
from scrapy_redis.connection import get_redis_conn 

from common.config import SpiderSourceCode,SpiderSourceName,RedisKeys,kafkaTopic
import logging
import shortuuid

class SinaIndividualStockPipeline(object):
    logger = logging.getLogger("htsc")

    def __init__(self):
        self.redis_conn=get_redis_conn()

    def process_item(self, item, spider):
        item["source"]=SpiderSourceName.sina
        item["type"]=SpiderSourceCode.individual_stock
        item["id"] = shortuuid.uuid()
        item["scope"] = u"个股"
        
        contents=AvroUtils.createAvroMemoryRecord(item,AvroUtils.getNewsSchema())
        kafka_producer.send(kafkaTopic.news,value=contents)
        sleep(1)
        self.logger.info("send data to kafka, from "+item["source"] +" , url: "+item["url"])
        get_redis_conn().zadd(RedisKeys.sina_individual_crawled,item["url"],item['pub_date'][0:10].replace("-",""))
        return item
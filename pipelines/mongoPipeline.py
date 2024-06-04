from datetime import datetime

import pymongo

from tutorial.itemVo.functionItemVo import FunctionItem
from tutorial.itemVo.liveSystemItemVo import LiveSystemItem

import json

from tutorial.itemVo.innovationItemVo import InnovationItem
from tutorial.itemVo.items import PdfItem
from tutorial.itemVo.strategyItemVo import StrategyItem
from tutorial.itemVo.apiPostDataVo import ApiPostDataItem


class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    # 正常插入，适用于item的value中里面不含类对象
    def insert_item(self, dbName, item):
        item['scrapy_time'] = datetime.strptime(item['scrapy_time'], "%Y-%m-%d %H:%M:%S")
        self.db[dbName].insert_one(json.loads(json.dumps(dict(item)).replace('\\u00a0', ' ')))

    # 转json插入，适用于item的value中里面含类对象，将对象转json
    def insert_item_with_json(self, dbName, item):
        data = json.loads(item.to_Json().replace('\\u00a0', ' '))['_values']
        data['scrapy_time'] = datetime.strptime(data['scrapy_time'], "%Y-%m-%d %H:%M:%S")
        self.db[dbName].insert_one(data)

    def process_item(self, item, spider):
        if isinstance(item, StrategyItem):
            self.insert_item_with_json('strategy', item)

        elif isinstance(item, ApiPostDataItem):
            spider.mongodbCname = 'api_data_taxo_cname'
            self.db['api_data_taxo_cname'].insert_one(dict(item))

        elif isinstance(item, InnovationItem):
            self.insert_item_with_json('innovation', item)

        elif isinstance(item, FunctionItem):
            self.insert_item('function', item)

        elif isinstance(item, LiveSystemItem):
            self.insert_item('live_system', item)

        elif isinstance(item, PdfItem):
            self.insert_item_with_json('mdpi', item)

        return item

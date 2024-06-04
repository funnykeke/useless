# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

from tutorial.itemVo.baseItem import BaseItem
from tutorial.itemVo.fileVo import FileVo


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    dept = scrapy.Field()
    name2 = scrapy.Field()
    introduction = scrapy.Field()
    timg = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    animal = scrapy.Field()
    type = scrapy.Field()
    author = scrapy.Field()
    timg2 = scrapy.Field()
    pass


class PdfItem(BaseItem):
    pdf = scrapy.Field()
    # 文献的标题
    name = scrapy.Field()
    # 文献作者
    authors = scrapy.Field()
    abstract = scrapy.Field()

    def __int__(self, *args, **kwargs):
        super(PdfItem, self).__init__(*args, **kwargs)
        self['pdf'] = None
        self['authors'] = []

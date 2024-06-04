import scrapy

from tutorial.itemVo.baseItem import BaseItem


class FunctionItem(BaseItem):
    name = scrapy.Field()
    slug = scrapy.Field()
    description = scrapy.Field()

    def __init__(self, *args, **kwargs):
        super(FunctionItem, self).__init__(*args, **kwargs)

import scrapy

from tutorial.itemVo.baseItem import BaseItem


class LiveSystemItem(BaseItem):
    name = scrapy.Field()
    slug = scrapy.Field()
    description = scrapy.Field()

    def __init__(self, *args, **kwargs):
        super(LiveSystemItem, self).__init__(*args, **kwargs)
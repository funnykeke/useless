import json
import scrapy

from tutorial.itemVo.baseItem import BaseItem


class InnovationItem(BaseItem):
    """基本信息部分"""
    language = scrapy.Field()
    image = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    keywords = scrapy.Field()
    label = scrapy.Field()
    balanceText = scrapy.Field()
    introText = scrapy.Field()
    imageVo = scrapy.Field()
    imageCredit = scrapy.Field()
    """定义字段属性"""
    function = scrapy.Field()
    patents = scrapy.Field()
    topic = scrapy.Field()
    benefits = scrapy.Field()
    applications = scrapy.Field()
    sdgs = scrapy.Field()
    """内容部分"""
    challenge = scrapy.Field()
    details = scrapy.Field()
    videos = scrapy.Field()
    imgs = scrapy.Field()
    story = scrapy.Field()
    references = scrapy.Field()
    """相关"""
    relatedPosts = scrapy.Field()
    termDefines = scrapy.Field()
    remain_request_count = scrapy.Field()

    def __init__(self, objectId, *args, **kwargs):
        super(InnovationItem, self).__init__(*args, **kwargs)
        self['objectId'] = objectId
        self['function'] = []
        self['patents'] = []
        self['benefits'] = []
        self['applications'] = []
        self['sdgs'] = []
        self['videos'] = []
        self['imgs'] = []
        self['references'] = []
        self['relatedPosts'] = []
        self['imageVo'] = None
        self['imageCredit'] = None
        self['termDefines'] = []


class Function(object):
    def __init__(self):
        self.name = ""
        self.describe = ""
        self.link = ""

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, allow_nan=False, sort_keys=False, indent=4)


class Patent(object):
    def __init__(self):
        self.url = ""
        self.name = ""
        self.size = ""
        self.type = ""

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, allow_nan=False, sort_keys=False, indent=4)


class Resource(object):
    def __init__(self):
        self.imageVo = None
        self.name = ""
        self.describe = ""
        self.link = ""

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, allow_nan=False, sort_keys=False, indent=4)


class Story(object):
    def __init__(self):
        self.describe = ""
        self.related_strategies = []

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, allow_nan=False, sort_keys=False, indent=4)


class RelatedStrategy(object):
    def __init__(self):
        self.link = ""
        self.pagename = ""
        self.animal = ""
        self.describe = ""


    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, allow_nan=False, sort_keys=False, indent=4)

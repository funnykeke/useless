import json
import scrapy

from tutorial.itemVo.baseItem import BaseItem
from tutorial.itemVo.baseVo import BaseVo


class StrategyItem(BaseItem):
    # 中文/英文
    language = scrapy.Field()
    pagename = scrapy.Field()
    type = scrapy.Field()
    url_html = scrapy.Field()
    describe = scrapy.Field()
    search_keyword = scrapy.Field()
    author = scrapy.Field()
    head_img = scrapy.Field()
    head_img_credit = scrapy.Field()
    """内容属性"""
    # living_system = scrapy.Field()
    functions = scrapy.Field()
    topic = scrapy.Field()
    introductions = scrapy.Field()
    key_list = scrapy.Field()
    keyIds = scrapy.Field()
    lastUpdate = scrapy.Field()
    animal = scrapy.Field()
    strategies = scrapy.Field()
    video = scrapy.Field()
    audio = scrapy.Field()
    potential = scrapy.Field()
    references = scrapy.Field()
    """相关"""
    related_posts = scrapy.Field()
    related_strategies = scrapy.Field()
    related_innovations = scrapy.Field()
    living_system = scrapy.Field()
    termDefines = scrapy.Field()
    remain_request_count = scrapy.Field()

    def __init__(self, objectId, *args, **kwargs):
        super(StrategyItem, self).__init__(*args, **kwargs)
        self['objectId'] = objectId
        self['functions'] = []
        self['topic'] = []
        self['introductions'] = []
        self['key_list'] = []
        self['keyIds'] = []
        self['video'] = []
        self['audio'] = []
        self['potential'] = []
        self['references'] = []
        self['related_posts'] = []
        self['related_strategies'] = []
        self['related_innovations'] = []
        self['strategies'] = {}
        self['living_system'] = {}
        self['termDefines'] = []

class referenceVo(BaseVo):
    def __init__(self):
        """基本信息部分"""
        # 一篇文章或书可能有多个引用句子
        self.sentence = []
        self.type = ""
        self.title = ""
        self.source = ""
        self.href = ''
        self.video = []


class functionVo(BaseVo):
    def __init__(self):
        self.name = ""
        self.describe = ""


class living_systemVo(BaseVo):
    def __init__(self):
        self.animal = ''
        self.animal_des = []
        self.more_this_system = ''
        self.img = None


class topicVo(BaseVo):
    def __init__(self):
        self.name = ''
        self.describe = ''
        self.link = ''
        self.img = None


class videoVo(BaseVo):
    def __init__(self):
        self.title = ''
        self.type = ''
        self.src = ''
        self.img = None
        self.describe = ''


class audioVo(BaseVo):
    def __init__(self):
        self.title = ''
        self.src = ''
        self.type = ''


class quoteVo(BaseVo):
    def __init__(self):
        self.sentence = ''
        self.cite = ''


class related_strategyVo(BaseVo):
    def __init__(self):
        self.url = ''
        self.img = None
        self.title = ''
        self.description = ''


class related_innovationVo(BaseVo):
    def __init__(self):
        self.url = ''
        self.img = None
        self.title = ''
        self.description = ''


class related_postVo(BaseVo):
    def __init__(self):
        self.url = ''
        self.img = None
        self.title = ''

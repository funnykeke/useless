import json
from datetime import datetime

import scrapy

from tutorial.itemVo.baseVo import BaseVo


class BaseItem(scrapy.Item, BaseVo):
    objectId = scrapy.Field()
    case_id = scrapy.Field()
    scrapy_time = scrapy.Field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['scrapy_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class TermDefine(object):
    def __init__(self):
        self.termDefineUrl = ''
        self.termDefineName = ''
        self.termDefineAudioUrl = ''
        self.termDefineDescription = ''
        self.termDefinePronunciation = ''

    def to_Json(self):
        return json.dumps(self, default=lambda o: o.__dict__, allow_nan=False, sort_keys=False, indent=4)

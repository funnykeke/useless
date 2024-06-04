import json

from tutorial.itemVo.baseVo import BaseVo


class ImageVo(BaseVo):

    def __init__(self):
        """基本信息部分"""
        self.id = ""
        self.src = ""
        self.path = ''
        self.srcset = ""
        self.alt = ""
        self.description = ""
        self.credit = None
        self.description = ''


class ImageCredit(BaseVo):

    def __init__(self):
        """基本信息部分"""
        self.credit = ""
        self.url = ""
        self.path = ''


class HeadImageVo(BaseVo):
    def __init__(self):
        self.id = ''
        self.src = ''
        self.srcset = ''
        self.alt = ''
        self.path = ''

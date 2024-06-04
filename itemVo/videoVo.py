import json

from tutorial.itemVo.ImageVo import ImageVo


class VideoVo(object):

    def __init__(self):
        """基本信息部分"""
        self.id = ""
        self.title = ""
        # self.type=""
        self.url = ""
        self.img = ImageVo()
        self.description = None

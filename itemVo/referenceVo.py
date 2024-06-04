import json

from tutorial.itemVo.baseVo import BaseVo


class ReferenceVo(BaseVo):

    def __init__(self):
        """基本信息部分"""
        # 一篇文章或书可能有多个引用句子
        self.sentence = []
        self.type = ""
        self.title = ""
        self.source = ""
        self.href = None

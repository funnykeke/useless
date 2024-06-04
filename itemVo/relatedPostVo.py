#!/usr/bin/env python3
import json

from tutorial.itemVo.baseVo import BaseVo
from tutorial.itemVo.ImageVo import ImageVo


class RelatedPostVo(BaseVo):

    def __init__(self):
        """基本信息部分"""
        self.url = ""
        self.title = ""
        self.description = ""
        self.img = ImageVo()

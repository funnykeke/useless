from tutorial.itemVo.baseVo import BaseVo


class FileVo(BaseVo):

    def __init__(self):
        """基本信息部分"""
        self.id = ""
        self.src = ""
        self.path = ''
        self.alt = ""
        self.description = ''
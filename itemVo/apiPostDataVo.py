import scrapy
import json

from tutorial.itemVo.baseItem import BaseItem


class ApiPostDataItem(BaseItem):
    postId = scrapy.Field()
    postType = scrapy.Field()
    postTypeLabel = scrapy.Field()
    postTitle = scrapy.Field()
    postDateInt = scrapy.Field()
    postModifiedInt = scrapy.Field()
    menuOrder = scrapy.Field()
    images = scrapy.Field()
    permalink = scrapy.Field()
    functionNames = scrapy.Field()
    systemNames = scrapy.Field()
    thumbnailUrl = scrapy.Field()
    publicDate = scrapy.Field()
    singularPostTypeLabel = scrapy.Field()
    summary = scrapy.Field()
    subTitle = scrapy.Field()
    content = scrapy.Field()
    sdg = scrapy.Field()
    innovationType = scrapy.Field()
    sector = scrapy.Field()
    stage = scrapy.Field()
    technology = scrapy.Field()
    academicStandards = scrapy.Field()
    academicSubject = scrapy.Field()
    audience = scrapy.Field()
    resourceType = scrapy.Field()
    reference_sources = scrapy.Field()
    # 本地保存的图片
    thumbnailUrl_href = scrapy.Field()

    taxonomies_hierarchical = scrapy.Field()
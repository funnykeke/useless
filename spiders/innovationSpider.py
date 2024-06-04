import sys
from pathlib import Path

sys.path.extend((str(parent.absolute()) for parent in Path(__file__).parents))
import json
from datetime import datetime

import scrapy
from scrapy import Request
from scrapy.cmdline import execute
from scrapy.utils.project import get_project_settings

from tutorial.itemVo.ImageVo import ImageVo, ImageCredit
from tutorial.itemVo.referenceVo import ReferenceVo
from tutorial.itemVo.relatedPostVo import RelatedPostVo
from tutorial.itemVo.videoVo import VideoVo
from tutorial.itemVo.innovationItemVo import InnovationItem, Function, Patent, Resource, Story, RelatedStrategy
from tutorial.utils.utils import MySQLUtil
from tutorial.itemVo.baseItem import TermDefine


class InnovationSpider(scrapy.Spider):
    name = "innovation"

    def __init__(self, taskInfo=None, *args, **kwargs):
        super(InnovationSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        self.mysql_util = MySQLUtil(settings.get('MYSQL_HOST'), settings.get('MYSQL_PORT'),
                                    settings.get('MYSQL_USER'), settings.get('MYSQL_PASSWORD'),
                                    settings.get('MYSQL_DATABASE'))
        if (taskInfo):
            self.task = json.loads(taskInfo)
            print('d', self.task)
        else:
            self.task = {}

    # 去除\xa0 和 换行
    def clear_str(self, str):
        if str:
            return str.replace(u'\xa0', u' ').strip()
        else:
            return ''

    def parser_baseInfo(self, response, item):
        url_txt = response.xpath('//*[@property="og:url"]/@content').get()
        imgStr = response.xpath('//*[@property="og:image"]/@content').get()
        title = response.xpath('//*[@property="og:title"]/@content').get().split(" \u2014 ")[0]
        contentWrap = response.xpath('//*[@id="content-wrap"]')
        content_Img = contentWrap.xpath('.//*[@class="lazyload"]')
        cont_img = ImageVo()
        cont_img.alt = content_Img.xpath('./@alt').get()
        cont_img.id = content_Img.xpath('./@data-id').get()
        cont_img.src = content_Img.xpath('./@data-src').get()
        cont_img.srcset = content_Img.xpath('./@data-srcset').get()
        image_credit = ImageCredit()
        head = response.xpath('.//*[@class="image-credit black-bg white-text"]')
        if head:
            a_tag = head.xpath('.//a')
            if a_tag:
                image_credit.url = a_tag.xpath('./@href').get()
            image_credit.credit = ''.join(head.xpath('.//text()').getall())
        typeNN = contentWrap[0].xpath('.//small/text()').get()
        balanceText = contentWrap[0].xpath('.//div[@class="wrap text-wrap post-hook subnav-section"]//q/p/text()').get()
        intro_Txt = contentWrap[0].xpath('.//*[@class="slide-bottom intro-text align-center fade"]/p/text()').get()
        item['url'] = url_txt
        item['image'] = imgStr
        item['title'] = title
        item['imageVo'] = cont_img
        item['imageCredit'] = image_credit
        item['label'] = typeNN
        item['balanceText'] = balanceText.replace(u'\u00a0', u' ') if balanceText else ''
        item['introText'] = intro_Txt.replace('\n', '', 2) if intro_Txt else ''
        # 关键字
        metaList = response.xpath('//meta')
        if len(metaList) > 13:
            item['keywords'] = metaList[13].xpath('./@content').get()
            item['description'] = metaList[12].xpath('./@content').get()
        return item

    def parser_functions(self, response, item):
        functions = response.xpath('//*[@id="post-functions"]')
        funsUser = []
        for fun in functions:
            funitem = fun.xpath('./div[contains(@class, "wrap")]')
            for it in funitem:
                fun1 = Function()
                fun1.name = it.xpath('.//h3/text()').get()
                fun1.describe = it.xpath('.//p/text()').get()
                # 旧版
                fun1.link = it.xpath('.//*[@class="button-wrap"]//a[@class="button search-button"][1]/@href').get()
                funsUser.append(fun1)
        item['function'] = funsUser
        # 解析专利
        docItems = response.xpath('//*[@id="post-documents"]//*[@class="download"]')
        patents = []
        for doc in docItems:
            p = Patent()
            p.url = doc.xpath('.//a[1]/@href').get()
            p.name = doc.xpath('.//strong[1]/text()').get()
            pstr = ''.join(doc.xpath('.//text()').getall()).replace('\n', '').replace(p.name, '')
            pudata = pstr.split(' ')
            p.size = ''.join(pudata[0:2])
            p.type = ''.join(pudata[2:])
            patents.append(p)
        item['patents'] = patents
        # 话题
        resources = response.xpath('//*[@id="post-resource"]//*[contains(@class, "wrap split toggle-split")]')
        resUsers = []
        for resource in resources:
            r = Resource()
            # 图片
            content_Img = resource.xpath('.//*[@class="lazyload"]')
            cont_img = ImageVo()
            cont_img.alt = content_Img.xpath('./@alt').get(),
            cont_img.id = content_Img.xpath('./@data-id').get(),
            cont_img.src = content_Img.xpath('./@data-src').get(),
            cont_img.srcset = content_Img.xpath('./@data-srcset').get()
            r.imageVo = cont_img
            r.name = resource.xpath('.//h3[1]/text()').get()
            r.describe = resource.xpath('.//p[1]/text()').get()
            r.link = resource.xpath('.//a[1]/@href').get()
            resUsers.append(r)
        item['topic'] = resUsers
        return item

    def parser_content(self, response, item):
        # 标题描述
        # title = response.xpath('//*[@id="post-content"]//q[1]/text()').get()
        # item['title'] = title

        # 子属性
        profileList = response.xpath('//*[contains(@class,"wrap text-wrap lite flush-top")]')

        for pp in profileList:
            pName = pp.xpath('.//h4[1]/text()').get()

            if 'Benefits' == pName or '好处' == pName or '好處' == pName:
                pListData = pp.xpath('.//*[@class="post-details"][1]//li')
                for i in pListData:
                    item['benefits'].append(i.xpath('./text()').get())
            elif 'Applications' == pName or '应用领域' == pName:
                pListData = pp.xpath('.//*[@class="post-details"][1]/li')
                for i in pListData:
                    item['applications'].append(i.xpath('./text()').get())
            elif 'UN Sustainable Development Goals Addressed' == pName or '联合国可持续发展目标的落实' == pName:
                pList = pp.xpath('.//*[@class="widont"]')
                for i in pList:
                    item['sdgs'].append(i.xpath('./text()').get())

            elif 'The Challenge' == pName or '挑战' == pName:
                item['challenge'] = ''.join(pp.xpath('.//p[1]//text()').getall())
            elif 'Innovation Details' == pName or '创新细节' == pName:
                item['details'] = ''.join(pp.xpath('.//p[1]//text()').getall())
        # 解析视频
        videos = response.xpath('//*[@id="video"]')
        if videos:
            videoData = self.parser_Video(videos[0].xpath('.//following-sibling::*[1]')[0])
            item['videos'].append(videoData)
        # 解析图片
        images = response.xpath('//*[@class="slideshow-layout"]')
        if images:
            imgList = images[0].xpath('.//*[@class="slide-wrap"]')
            for imgItem in imgList:
                img = ImageVo()
                img.src = imgItem.xpath('.//a/@href').get(),
                img.creditBy = imgItem.xpath('.//*[@class="image-credit black-bg white-text"]/text()').get()
                item['imgs'].append(img)
        # 故事
        story1 = response.xpath('//*[@id="biological-model"]')
        story2 = response.xpath('//*[@id="biomimicry-story"]')
        story = story1 if story1 else story2
        if story:
            storyObj = Story()
            itemStory = story.xpath('.//following-sibling::*[1]')
            h4Obj = itemStory.xpath('./h4[1]')[0]
            storyObj.describe = ''.join(h4Obj.xpath('./following-sibling::p/text()').getall())
            if itemStory[0].xpath('.//*[@class="inline-button"]'):
                strategies = itemStory[0].xpath('''//*[@class="panel-content posts"]/div[@class='preview strategy']''')
                for strategy in strategies:
                    related_strategy = RelatedStrategy()
                    related_strategy.link = strategy.xpath('./a/@href').get()
                    related_strategy.pagename = strategy.xpath('./a//div[@class="preview-details"]/h4/text()').get()
                    related_strategy.animal = strategy.xpath('./a//div[@class="preview-details"]/p/text()').get()
                    related_strategy.describe = strategy.xpath('./a//div[@class="preview-description"]/p/text()').get()
                    storyObj.related_strategies.append(related_strategy)
            item['story'] = storyObj
        # 引用
        item = self.parser_references(response, item)
        # 相关
        return self.parser_related_posts(response, item)

    def parser_Video(self, article):
        videoImg = ImageVo()
        video = VideoVo()
        videoBar = article.xpath('.//figure[@class="video-wrap no-size"]')
        if videoBar:
            payBtn = article.xpath('.//button[@class="play-toggle"]')
            if payBtn.xpath('./@data-player'):
                player = payBtn.xpath('./@data-player').get()
                if player == 'youtube':
                    videoImg.src = article.xpath('.//img/@src').get()
                    videoImg.alt = article.xpath('.//img/@alt').get()
                    video.videoid = payBtn[0].xpath('./@data-videoid').get()
                    video.src = article.xpath('.//iframe/@src').get()
                    video.type = player
            elif payBtn.xpath('./@data-videourl'):
                player = payBtn.xpath('@data-videourl').get()
                if payBtn.xpath('./@data-videoid'):
                    video.videoid = payBtn.xpath('./@data-videoid').get()
                imgData = article.xpath('.//img')
                if imgData.xpath('./@src'):
                    videoImg.src = imgData.xpath('./@src').get()
                else:
                    videoImg.src = imgData.xpath('./@data-src').get()
                    videoImg.id = imgData.xpath('./@data-id').get()
                    videoImg.srcset = imgData.xpath('./@data-srcset').get()
                videoImg.alt = article.xpath('.//img/@alt').get()
                video.src = player
        video.img = videoImg
        return video

    def parser_references(self, response, item):
        txt = response.xpath('//*[@id="references-content"]')
        if txt:
            for i in response.xpath('//dd'):
                reference = ReferenceVo()
                source_meta = i.xpath('.//*[@class="source-meta"]')
                if source_meta:
                    # for text in i.xpath('./p/text()').getall():
                    #     reference.sentence.append(self.clear_str(text))
                    # 检查有无句子,句子可能有多个
                    tag_txt = i.xpath('.//following-sibling::*[1]')
                    tag = tag_txt.xpath('name()').get()

                    # tag_txt = i.xpath('./following-sibling::*[1]')
                    # tag = tag_txt[0].tag if tag_txt else ''
                    while tag == 'p':
                        reference.sentence.append(tag_txt[0].xpath('./text()').get())
                        tag_txt = tag_txt[0].xpath('following-sibling::*[1]')
                        if tag_txt:
                            tag = tag_txt[0].tag
                        else:
                            break

                    small = source_meta.xpath('./small')
                    if small:
                        reference.type = small.xpath('.//text()').get()

                    h4 = source_meta.xpath('./h4')
                    if h4:
                        reference.title = self.clear_str(h4.xpath('.//text()').get())

                    p = source_meta.xpath('./p')
                    if p:
                        reference.source = self.clear_str(p.xpath('.//text()').get())

                    embedly_card = source_meta.xpath('.//a[@class="embedly-card"]')
                    if embedly_card:
                        reference.href = embedly_card.xpath('./@href').get()

                item['references'].append(reference)
        return item

    def parser_related_posts(self, response, item):
        txt = response.xpath('//*[@id="related-posts"]')
        if txt:
            for i in txt[0].xpath('.//*[@class="preview innovation"]'):
                related_post = RelatedPostVo()
                img = ImageVo()
                url = i.xpath('.//a[1]/@href').get()
                img_txt = i.xpath('.//img[@class="lazyload"]')
                if img_txt:
                    img.alt = img_txt[0].xpath('./@alt').get()
                    img.id = img_txt[0].xpath('./@data-id').get()
                    img.src = img_txt[0].xpath('./@data-src').get()
                    img.srcset = img_txt[0].xpath('./@data-srcset').get()
                    related_post.url = url
                    related_post.img = img
                    title = i.xpath('.//div[@class="preview-details"][1]//h4[1]/text()').get()
                    description = i.xpath('.//div[@class="preview-description"][1]//p[1]/text()').get()
                    related_post.title = title
                    related_post.description = description
                    item['relatedPosts'].append(related_post)
        return item

    def parser_term_define(self, response):
        item = response.meta['item']
        termDefine = TermDefine()
        termDefine.termDefineUrl = response.meta['originalUrl']
        termDefine.termDefineName = response.xpath("//div[@id='term-definition']/h3/text()").get()
        termDefine.termDefineAudioUrl = response.xpath("//div[@id='term-definition']/audio/source/@src").get()
        termDefine.termDefinePronunciation = response.xpath("//div[@id='term-definition']/p[1]/text()").get()
        termDefine.termDefineDescription = response.xpath("//div[@id='term-definition']/p[2]/text()").get()
        if not (termDefine.termDefinePronunciation.endswith('/') and termDefine.termDefinePronunciation.startswith(
                '/')):
            termDefine.termDefineDescription = termDefine.termDefinePronunciation
            termDefine.termDefinePronunciation = None
        item['termDefines'].append(termDefine)
        item['remain_request_count'] -= 1
        if item['remain_request_count'] == 0:
            del item['remain_request_count']
            yield item
            scrapy_time = datetime.strptime(item['scrapy_time'], "%Y-%m-%d %H:%M:%S")
            self.mysql_util.execute_update("update CASE_SCRAPY_URL set STATUS='1', SCRAPY_DATE=%s"
                                           " where URL_ID=%s",
                                           (scrapy_time, response.meta['url_id'],))

    def handle_error(self, failure):
        item = failure.request.meta['item']
        item['remain_request_count'] -= 1
        if item['remain_request_count'] == 0:
            del item['remain_request_count']
            yield item
            scrapy_time = datetime.strptime(item['scrapy_time'], "%Y-%m-%d %H:%M:%S")
            self.mysql_util.execute_update("update CASE_SCRAPY_URL set STATUS='1', SCRAPY_DATE=%s where URL_ID=%s",
                                           (scrapy_time, failure.request.meta['url_id'],))

    def start_requests(self):
        results = self.mysql_util.execute_query(
            f"select URL_ID, URL_STR, OBJECT_ID from CASE_SCRAPY_URL where CASE_ID={self.task['caseId']} AND STATUS='0' "
            f"AND POST_TYPE='innovation'")
        for result in results:
            link = result[1]
            if self.task['lan'] in ['ZH', 'ALL']:
                zh_link = link.replace('https://asknature.org/', 'https://asknature.org/zh-CN/')
                yield Request(zh_link, callback=self.parse,
                              meta={'objectID': result[2], 'caseId': self.task['caseId'], 'url_id': result[0],
                                    'lan': 'ZH'})
            if self.task['lan'] in ['EN', 'ALL']:
                yield Request(link, callback=self.parse,
                              meta={'objectID': result[2], 'caseId': self.task['caseId'], 'url_id': result[0],
                                    'lan': 'EN'})

    def parse(self, response, **kwargs):
        item = InnovationItem(response.meta['objectID'])
        item['language'] = response.meta['lan']
        item = self.parser_baseInfo(response, item)
        item = self.parser_functions(response, item)
        item = self.parser_content(response, item)
        item['case_id'] = int(response.meta['caseId'])
        term = response.xpath("//p//button[@title='See term definition']")
        if not term:
            term = response.xpath("//p//button[@title='参见术语定义']")
        if term:
            item['remain_request_count'] = len(term)
            for index, i in enumerate(term):
                termDefineUrl = i.xpath('./@data-term').get()
                if not termDefineUrl.endswith('/'):
                    termDefineUrl = termDefineUrl + '/'
                if termDefineUrl:
                    yield Request(url=termDefineUrl, errback=self.handle_error, dont_filter=True, callback=self.parser_term_define,
                                  meta={'item': item, 'url_id': response.meta['url_id'], 'originalUrl': termDefineUrl})
        else:
            yield item
            scrapy_time = datetime.strptime(item['scrapy_time'], "%Y-%m-%d %H:%M:%S")
            self.mysql_util.execute_update("update CASE_SCRAPY_URL set STATUS='1', SCRAPY_DATE=%s"
                                           " where URL_ID=%s",
                                           (scrapy_time, response.meta['url_id'],))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process command line arguments')
    parser.add_argument('--case_id', type=str, default='8', help='Case ID parameter')
    parser.add_argument('--lan', default='ALL', type=str, help='lan parameter (zh or en) en default')
    args = parser.parse_args()
    case_id = args.case_id
    lan = args.lan
    par = {
        "caseId": case_id,
        "lan": lan if lan else 'EN'
    }
    execute(['scrapy', 'crawl', 'innovation', '-a', "taskInfo=" + json.dumps(par)])

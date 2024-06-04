import sys
from pathlib import Path

sys.path.extend((str(parent.absolute()) for parent in Path(__file__).parents))
import calendar
import json
from datetime import datetime
import scrapy
from scrapy import Request
from scrapy.cmdline import execute
from scrapy.utils.project import get_project_settings

from tutorial.itemVo.ImageVo import ImageCredit, ImageVo, HeadImageVo
from tutorial.itemVo.strategyItemVo import functionVo, living_systemVo, topicVo, videoVo, audioVo, \
    related_innovationVo, quoteVo, related_strategyVo, related_postVo, referenceVo, StrategyItem
from tutorial.utils.utils import MySQLUtil
from tutorial.itemVo.baseItem import TermDefine


class StrategySpider(scrapy.Spider):
    name = "strategy"

    def __init__(self, taskInfo=None, *args, **kwargs):
        super(StrategySpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        if (taskInfo):
            self.task = json.loads(taskInfo)
            print('d', self.task)
        else:
            self.task = {}
        self.mysql_util = MySQLUtil(settings.get('MYSQL_HOST'), settings.get('MYSQL_PORT'),
                                    settings.get('MYSQL_USER'), settings.get('MYSQL_PASSWORD'),
                                    settings.get('MYSQL_DATABASE'))

    ################解析############
    # 去除\xa0 和 换行
    def clear_str(self, str):
        if str:
            return str.replace(u'\xa0', u' ').strip()
        else:
            return ''

    def add_keyIds(self, key, item):
        if key not in item['keyIds']:
            item['keyIds'].append(key)
        return item

    # 解析introduction
    def parser_introduction(self, article, item):
        for p in article.xpath('.//p/text()').getall():
            introduction = self.clear_str(p)
            item['introductions'].append(introduction)
        return item

    # 解析策略
    def parser_strategy(self, article, item):
        strategies = []
        for p in article.xpath('.//p/text()').getall():
            strategy = self.clear_str(p)
            if strategy.strip():
                strategies.append(strategy)
        item['strategies']['the_strategy'] = strategies
        return self.add_keyIds('the_strategy', item)

    # 解析相关策略
    def parser_related_strategies(self, article, item):
        # print('related_strategies:  ',end='')
        for i in article.xpath('.//*[@class="preview strategy"]'):
            img = ImageVo()
            related_strategy = related_strategyVo()
            url = i.xpath('.//a[1]/@href').get()
            # #print(url)
            # 背景图片
            img_txt = i.xpath('.//img[@class="lazyload"]')
            if img_txt:
                img.alt = img_txt[0].xpath('./@alt').get()
                img.id = img_txt[0].xpath('./@data-id').get()
                img.src = img_txt[0].xpath('./@data-src').get()
                img.srcset = img_txt[0].xpath('./@data-srcset').get()
            related_strategy.url = url
            related_strategy.img = img

            title = i.xpath('.//div[@class="preview-details"]/h4[1]/text()').get()
            description = i.xpath('.//div[@class="preview-description"]/p[1]/text()').get()
            related_strategy.title = self.clear_str(title)
            related_strategy.description = self.clear_str(description)
            item['related_strategies'].append(related_strategy)
        return item
        # #print(related_strategy)
        # print(self.content['related_strategies'])

    # 解析搜索关键字
    def sarch_keyword(self, response, item):
        item['search_keyword'] = response.xpath('(//meta)[14]/@content').get()
        return item

    # 解析潜力
    def parser_potential(self, article, item):
        for p in article.xpath('.//p/text()').getall():
            potential = self.clear_str(p)
            item['potential'].append(potential)
        return item

    # 解析article中的视频
    def parser_video(self, article, media_type, item):
        img = ImageVo()
        video = videoVo()

        video_title = article.xpath('.//h4/text()').get()
        if video_title:
            video.title = self.clear_str(video_title)

        if article.xpath(".//figure[contains(@class,'video-wrap') and contains(@class,'no-size')]"):
            video_src = article.xpath('.//button[@class="play-toggle"]/@data-videourl').get()
            if not video_src:
                video_src = 'https://www.youtube.com/embed/' + article.xpath(
                    './/button[@class="play-toggle"]/@data-videoid').get()
            img_src = article.xpath('.//img/@src').get() or article.xpath('//img/@data-src').get()
            img_alt = article.xpath('.//img/@alt').get()

            img.src = img_src
            img.alt = img_alt

        elif article.xpath('.//figure[@class="video-wrap"]'):
            video_src = article.xpath('.//video/@data-video').get()
            img_txt = article.xpath('.//img[@class="lazyload"]')
            if img_txt:
                img.src = img_txt.xpath('./@data-src').get()
                img.alt = img_txt.xpath('./@alt').get()
                img.id = img_txt.xpath('./@data-id').get()
                img.srcset = img_txt.xpath('./@data-srcset').get()

            if article.xpath('.//p/text()'):
                video.title = article.xpath('.//p/text()').get()

        elif article.xpath('.//iframe'):
            video_src = article.xpath('.//iframe/@src').get()
        else:
            return item
        video.type = media_type
        video.src = video_src
        video.img = img
        # 视频的描述信息
        video_description = article.xpath('.//p/text()').get()
        if video_description:
            video.describe = video_description
        item['video'].append(video)
        if media_type not in item['keyIds']:
            item = self.add_keyIds(media_type, item)
        return item

    # 解析音频
    def parser_audio(self, article, item):
        # 使用XPath表达式选取音频数据
        audio_title = article.xpath('.//h4/text()').get()
        audio_src = article.xpath('.//source/@src').get()
        audio_type = article.xpath('.//source/@type').get()

        # 创建并填充audioVo对象
        audio = audioVo()
        audio.title = audio_title
        audio.src = audio_src
        audio.type = audio_type

        # 将audio对象添加到item中
        item['audio'].append(audio)
        return item

    # 解析content中img
    def parser_image(self, article, item):
        # 使用XPath表达式选取所有滚动图
        wrap = article.xpath('.//div[@class="slide-wrap"]')

        # 初始化存储滚动图的列表
        if 'imgs' not in item['strategies']:
            item['strategies']['imgs'] = []

        for w in wrap:
            img = ImageVo()
            img_txt = w.xpath('.//img')
            p_txt = w.xpath('.//p//text()')
            img.alt = img_txt.xpath('./@alt').get()
            img.id = img_txt.xpath('./@data-id').get()
            img.src = img_txt.xpath('./@data-src').get()

            if p_txt:
                img.describe = self.clear_str(p_txt.get())

            try:
                img.srcset = img_txt.xpath('./@data-srcset').get()
            except:
                print("图片id:%s没有'srcset'" % img.id)

            item['strategies']['imgs'].append(img)

        return self.add_keyIds('imgs', item)

    # 解析相关发明、创新
    def parser_related_innovation(self, article, item):
        # related_innovations = []
        for i in article.xpath('.//*[@class="preview innovation"]'):
            related_innovation = related_innovationVo()

            # 提取链接
            url = i.xpath('.//a[1]/@href').get()
            # 背景图片
            img = ImageVo()
            if i.xpath('.//img[@class="lazyload"]'):
                img_txt = i.xpath('.//img[@class="lazyload"]')
                img.alt = img_txt.xpath('./@alt').get()
                img.id = img_txt.xpath('./@data-id').get()
                img.src = img_txt.xpath('./@data-src').get()
                img.srcset = img_txt.xpath('./@data-srcset').get()

            related_innovation.url = url
            related_innovation.img = img

            # 提取标题和描述信息
            title = i.xpath('.//div[@class="preview-details"]//h4[1]/text()').get()
            description = i.xpath('.//div[@class="preview-description"]//p[1]/text()').get()

            related_innovation.title = self.clear_str(title)
            related_innovation.description = self.clear_str(description)

            # related_innovations.append(dict(related_innovation))

            item['related_innovations'].append(related_innovation)
        return item

    # 解析搜索关键字
    def parser_search_keyword(self, response, item):
        search_keyword = response.xpath('//meta[@name="keywords"]/@content').get()
        item['search_keyword'] = search_keyword
        return item

    # 解析大标题部分
    def parser_head(self, response, item):
        head = response.xpath(
            "//*[@class='fullscreen post-hero strategy-hero vertical-center light-green-bg white-text']")
        txt = head.xpath(".//h2[@class='widont serif balance-text']")
        pagename = txt.xpath('./text()').get()
        item['pagename'] = self.clear_str(pagename)

        animal = txt.xpath('./following-sibling::*/text()[1]').get()
        if animal:
            item['animal'] = animal

        type = response.xpath('//div[@class="slide-top align-center fade"]/small/text()').get()
        item['type'] = type

        author = response.xpath('//div[@class="slide-bottom intro-text align-center fade"]/p/text()').get()
        item['author'] = author

        image_credit = ImageCredit()
        credit = head.xpath('.//*[@class="image-credit black-bg white-text"]//text()').getall()
        if credit:
            image_credit.credit = ''.join(credit)
            url = head.xpath('.//*[@class="image-credit black-bg white-text"]/a/@href').get()
            if url:
                image_credit.url = url
        item['head_img_credit'] = image_credit
        img = HeadImageVo()
        img_txt = head.xpath('.//img')
        if img_txt:
            img.id = img_txt.xpath('./@data-id').get()
            img.src = img_txt.xpath('./@data-src').get()
            img.srcset = img_txt.xpath('./@data-srcset').get()
            img.alt = img_txt.xpath('./@alt').get()
            item['head_img'] = img
        return item

    def parser_key_list(self, response, item):
        sub2 = response.xpath('//nav[@class="subnav toc" and @id="subnav"]//a')
        item['key_list'] = sub2.xpath('text()').getall()
        if item['strategies'] and ('The strategy' and '战略' not in item['key_list']):
            if item['language'] == 'EN':
                item['key_list'].append('The strategy')
            else:
                item['key_list'].append('战略')
        return item

    def parser_html_url(self, response, item):
        url_html = response.xpath('//meta[@property="og:url"]/@content').get()
        item['url_html'] = url_html
        return item

    # 解析功能
    def parser_functions(self, response, item):
        funcs = response.xpath('//*[@id="post-functions"][1]//h3[@class="widont"]')
        for func in funcs:
            function = functionVo()
            function.name = func.xpath('./text()').get()
            function.describe = self.clear_str(func.xpath('following-sibling::*/text()').get())
            item['functions'].append(function)
        return item

    # 检查上次更新时间
    def check_updata(self, lastUpdate, item):
        # print('lastupdata:  ',end='')
        if lastUpdate:
            update_time = lastUpdate.xpath('./text()').get()[13:]
            # 获取月份所在索引
            index = update_time.find(' ')
            # 获取英文月份
            english_month = update_time[:index]
            # 将英文月份转换为数字
            month = list(calendar.month_name).index(english_month)
            # 组合形成数字时间
            update_time = update_time[index:] + ',' + str(month)
            # #print(update_time)
            update_time = datetime.strptime(update_time, ' %d, %Y,%m')
            # 生成时间戳
            # print(update_time)
            # #print(update_time.timestamp())
            item['lastUpdate'] = update_time.timestamp()
        return item

    def parser_living_system(self, response, item):
        live = living_systemVo()
        txt = response.xpath('//*[@id="post-systems"]')
        if txt:
            text = txt.xpath('.//*[@class="wrap text-wrap"]')
            live.animal = text.xpath('.//h3/text()').get()
            live.animal_des = text.xpath('.//p/text()').getall()
            live.more_this_system = text.xpath('.//*[@class="inline-button"]/@href').get()
            img = ImageVo()
            img_txt = txt.xpath('.//img')
            if img_txt:
                img.alt = img_txt.xpath('./@alt').get()
                img.id = img_txt.xpath('./@data-id').get()
                img.src = img_txt.xpath('./@data-src').get()
                img.srcset = img_txt.xpath('./@data-srcset').get()
                live.img = img
            item['living_system'] = live
        return item

    def parser_topic(self, response, item):
        topic = topicVo()
        txt = response.xpath('//*[@id="post-resource"]')
        if txt:
            text = txt.xpath('.//*[contains(@class,"wrap text-wrap")]')
            topic.name = text.xpath('.//h3/text()').get()
            topic.describe = self.clear_str(text.xpath('.//p/text()').get())
            topic.link = text.xpath('.//*[@class="inline-button"]/@href').get()
            img_txt = txt.xpath('.//img')
            if img_txt:
                img = ImageVo()
                img.alt = img_txt.xpath('./@alt').get()
                img.id = img_txt.xpath('./@data-id').get()
                img.src = img_txt.xpath('./@data-src').get()
                img.srcset = img_txt.xpath('./@data-srcset').get()
                topic.img = img
            item['topic'].append(topic)
        return item

    def parser_section_content(self, response, item):
        section = response.xpath('//section[@id="post-content"]')
        if section.xpath(".//div[contains(@class, 'wrap text-wrap post-hook')]"):
            # 获取描述
            describe = ''.join(response.xpath("//div[contains(@class, 'wrap text-wrap post-hook')]/q//text()").getall())
            item['describe'] = self.clear_str(describe)

        # 获取所有article元素
        articles = section.xpath('.//article')
        now_content = ''

        for article in articles:
            class_name = article.xpath('./@class').get()

            if class_name == 'text-layout':
                now_content = article.xpath('.//div[@class="page-anchor"]/@id').get()

                if now_content == 'introduction':
                    item = self.parser_introduction(article, item)

                elif now_content == 'the-strategy':
                    item = self.parser_strategy(article, item)

                elif now_content == 'the-potential':
                    item = self.parser_potential(article, item)
                elif 'section' in now_content:
                    if article.xpath('.//div[@class="panel-title"]'):
                        button = {}
                        strategy = {}
                        button['title'] = article.xpath('.//div[@class="panel-title"]//h4/text()').get()
                        button['src'] = article.xpath('.//div[@class="panel-title"]//svg/@xmlns').get()
                        button['strategy_title'] = article.xpath(
                            './/div[@class="preview strategy"]//h4[@class="widont"]/text()').get()
                        button['href'] = article.xpath('.//div[@class="preview strategy"]//a/@href').get()
                        item['strategies'][now_content] = button
                        item = self.add_keyIds(now_content, item)
                        # print(button)
                    # 文本内容 归入strategies
                    elif article.xpath('.//p'):
                        p_text = []
                        for p in article.xpath('.//p'):
                            text = ''.join(p.xpath('.//text()').getall())
                            if text and 'Watch Video' in text:
                                video = videoVo()
                                video.type = now_content
                                video.src = p.xpath('.//a/@href').get()
                                item['video'].append(video)
                            p_text.append(text)
                        item['strategies'][now_content] = p_text
                        item = self.add_keyIds(now_content, item)
                        # #print(self.content['strategies'][now_content])
                    else:
                        print("%s section类型没有处理" % now_content)
                else:
                    print("%s section类型没有处理" % now_content)
            # 解析content的媒体内容
            elif 'media-layout' in class_name:
                media_type = article.xpath('.//div[@class="page-anchor"]/@id').get()

                if media_type == 'video' or 'see-' in media_type or 'look' in media_type:
                    item = self.parser_video(article, media_type, item)

                elif 'listen-' in media_type:
                    item = self.add_keyIds(media_type, item)
                    item = self.parser_audio(article, item)

                elif media_type == 'the-strategy':
                    item = self.parser_strategy(article, item)
                    item = self.parser_video(article, media_type, item)
                elif media_type == 'the-potential':
                    item = self.parser_potential(article, item)
                    item = self.parser_video(article, media_type, item)
                else:
                    item = self.parser_video(article, media_type, item)
            # 解析图片的内容
            elif class_name == 'slideshow-layout':
                if article.xpath('.//img'):
                    item = self.parser_image(article, item)
            # 引用内容
            elif class_name == 'quote-layout':
                if 'quote' not in item['strategies'].keys():
                    item['strategies']['quote'] = []

                content_quote = quoteVo()
                content_quote.sentence = self.clear_str(article.xpath('.//q[@class="widont"]//text()').get())
                if article.xpath('.//cite'):
                    content_quote.cite = article.xpath('.//cite//text()').get()
                item['strategies']['quote'].append(content_quote)
                item = self.add_keyIds('quote', item)
            # 相关内容
            elif 'posts-layout' in class_name:
                type = article.xpath('.//div[@class="page-anchor"]/@id').get()

                if 'related-strateg' in type:
                    item = self.parser_related_strategies(article, item)
                elif 'related-innovation' in type:
                    item = self.parser_related_innovation(article, item)
                elif article.xpath('.//h4'):
                    if article.xpath('.//h4/text()').get() == 'Related Strategies':
                        item = self.parser_related_strategies(article, item)
                    elif article.xpath('.//h4/text()').get() == 'Related Innovation':
                        item = self.parser_related_innovation(article, item)
                    else:
                        item = self.parser_related_strategies(article, item)
                else:
                    item = self.parser_related_strategies(article, item)
            else:
                print("%s类型没有处理" % now_content)
        update = response.xpath("//*[@class='wrap text-wrap flush-top' and not(@id)]/h5")
        return self.check_updata(update, item)

    # 解析相关推送
    def parser_related_posts(self, response, item):
        txt = response.xpath('//*[@id="related-posts"]')
        if txt:
            for i in txt[0].xpath('.//div[@class="preview strategy"]'):
                related_post = related_postVo()
                img = ImageVo()
                url = i.xpath('.//a[1]/@href').get()
                # 背景图片
                img_txt = i.xpath('.//img[@class="lazyload"]')
                if img_txt:
                    img.alt = img_txt[0].xpath('./@alt').get()
                    img.id = img_txt[0].xpath('./@data-id').get()
                    img.src = img_txt[0].xpath('./@data-src').get()
                    img.srcset = img_txt[0].xpath('./@data-srcset').get()

                    related_post.url = url
                    related_post.img = img

                    title = i.xpath('.//div[@class="preview-details"]/h4[1]/text()').get()
                    description = i.xpath('.//div[@class="preview-description"]/p[1]/text()').get()

                    related_post.title = self.clear_str(title)
                    related_post.description = self.clear_str(description)
                    item['related_posts'].append(related_post)
        return item

    # 解析引用内容，可能有多个引用，有的有句子 有的没有
    def parser_references(self, response, item):
        if response.xpath("//div[@id='references-content']"):
            for dd in response.xpath('//dd'):
                reference = referenceVo()
                source_meta = dd.xpath('.//*[@class="source-meta"]')

                if source_meta:
                    # 检查是否有句子,句子可能有多个
                    tag_txt = dd.xpath('.//following-sibling::*[1]')
                    tag = tag_txt.xpath('name()').get()
                    while tag == 'p':
                        sentence = self.clear_str(tag_txt.xpath('string()').get())
                        if sentence == 'Watch Video':
                            video = videoVo()
                            video.src = tag_txt.xpath('.//a/@href').get()
                            reference.video.append(video)
                        reference.sentence.append(sentence)
                        tag_txt = tag_txt.xpath('following-sibling::*[1]')
                        tag = tag_txt.xpath('name()').get()

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

    # 解析更多
    def parser_more_from_system(self, response, item):
        systems = response.xpath("//ul[@class='breadcrumb']/li/a/text()").getall()
        name = response.xpath("//div[@id='post-systems']//h3/text()").get()
        # for system in systems:
        #     if system in name:
        #         name = system
        #         break
        if name in systems:
            name_index = systems.index(name)
            parents = systems[:name_index]
            children = systems[name_index + 1:]
        else:
            parents = []
            children = []
        taxon = response.xpath("//div[@id='post-systems']//h3/following-sibling::p[1]/text()").get()
        if taxon:
            taxon = taxon.split(': ')
            if len(taxon) > 1:
                taxon = taxon[1].split(', ')
            taxon = '-'.join(taxon)
        description = response.xpath("//div[@id='post-systems']//h3/following-sibling::p[2]/text()").get()
        img_txt = response.xpath('//div[@id="post-systems"]//img')
        img = ImageVo()
        if img_txt:
            img.alt = img_txt.xpath('./@alt').get()
            img.id = img_txt.xpath('./@data-id').get()
            img.src = img_txt.xpath('./@data-src').get()
            img.srcset = img_txt.xpath('./@data-srcset').get()
        item['living_system'] = {'name': name, 'taxon': taxon, 'description': description, 'parents': parents,
                                 'children': children, 'img': img}
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
            f"AND POST_TYPE='strategy'")
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
        item = StrategyItem(response.meta['objectID'])
        item['language'] = response.meta['lan']
        # 解析页面的url
        item = self.parser_html_url(response, item)
        # 解析 查找关键字
        item = self.sarch_keyword(response, item)
        #### 解析头部#########################
        item = self.parser_head(response, item)
        # 解析functions#############################
        item = self.parser_functions(response, item)
        # 解析生命系统###################
        # item = self.parser_living_system(response, item)
        # 解析topic
        item = self.parser_topic(response, item)
        # section
        item = self.parser_section_content(response, item)
        # 解析References
        item = self.parser_references(response, item)
        # 解析推送
        item = self.parser_related_posts(response, item)
        # 解析key_list
        item = self.parser_key_list(response, item)
        # 解析更多
        item = self.parser_more_from_system(response, item)
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
    parser.add_argument('--case_id', default='8', type=str, help='Case ID parameter')
    parser.add_argument('--lan', default='ALL', type=str, help='lan parameter (zh or en) en default')
    args = parser.parse_args()
    case_id = args.case_id
    lan = args.lan
    par = {
        "caseId": case_id,
        "lan": lan if lan else 'EN'
    }
    execute(['scrapy', 'crawl', 'strategy', '-a', "taskInfo=" + json.dumps(par)])

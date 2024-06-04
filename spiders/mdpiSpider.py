import sys
from pathlib import Path

sys.path.extend((str(parent.absolute()) for parent in Path(__file__).parents))

import json
from scrapy.cmdline import execute
import scrapy
from tutorial.itemVo.fileVo import FileVo
from tutorial.itemVo.items import PdfItem



class StrategySpider(scrapy.Spider):
    name = "mdpi"
    custom_settings = {
        # # 开启cookie
        # 'COOKIES_ENABLED': True,
        # # 关闭重复请求过滤
        # 'DUPEFILTER_CLASS': 'tutorial.filter.CloseDupeFilter',
        # 'CONCURRENT_REQUESTS': 1,
    }
    '''
    要求的taskInfo格式：
    按关键词爬取
    {
        "caseId": "40852",
        "taskId": '111',
        "stepId": '111',
        "keywords": "knowledge",
        # 不写max_page表示全爬
        "max_page": 2
    }
    按生物栏目爬取
    {
        "caseId": "40852",
        "taskId": '111',
        "stepId": '111'
        # 不写max_page表示全爬
        "max_page": 2
    }
    '''

    def __init__(self, taskInfo=None, *args, **kwargs):
        super(StrategySpider, self).__init__(*args, **kwargs)
        if taskInfo:
            self.task = json.loads(taskInfo)
            print('d', self.task)
        else:
            self.task = {}

    def start_requests(self):
        if 'keywords' in self.task.keys():
            yield scrapy.Request(url=f'https://www.mdpi.com/search?q={self.task["keywords"]}&page_count=10',
                                 callback=self.parse_search, meta={
                    'max_page': None if 'max_page' not in self.task.keys() else self.task['max_page']})
        else:
            yield scrapy.Request(url=f'https://www.mdpi.com/search?page_count=10&journal=biomimetics',
                                 callback=self.parse_search, meta={
                    'max_page': None if 'max_page' not in self.task.keys() else self.task['max_page']})

    # 按关键词搜索文献
    def parse_search(self, response, **kwargs):
        links = response.xpath("//a[@title='Article PDF']/@href").getall()
        names = response.xpath("//a[@title='Article PDF']/@data-name").getall()
        author_divs = response.xpath("//a[@title='Article PDF']/parent::div/parent::div/div[@class='authors']")
        authors = []
        for author_div in author_divs:
            authors.append('&'.join(author_div.xpath(".//span[@class='sciprofiles-link__name']/text()").getall()))
        abstract_divs = response.xpath(
            "//a[@title='Article PDF']/parent::div/parent::div/div[@class='abstract-div']")
        abstracts = []
        for abstract_div in abstract_divs:
            abstracts.append(
                ''.join(abstract_div.xpath("./div[@class='abstract-full ']//text()").getall()).strip().strip(
                    'Full article'))
        for index, link in enumerate(links):
            # fileVo = FileVo()
            # fileVo.src = response.urljoin(link)
            pdfItem = PdfItem()
            # pdfItem['pdf'] = fileVo
            pdfItem['name'] = names[index]
            pdfItem['authors'] = authors[index].split('&')
            pdfItem['abstract'] = abstracts[index]
            pdfItem['case_id'] = int(self.task['caseId'])
            yield scrapy.Request(url=response.urljoin(link), callback=self.capture_redirect,
                                 meta={'index': index, 'pdfItem': pdfItem, 'dont_redirect': True, 'handle_httpstatus_list': [302]})
            # yield pdfItem
        if 'max_page' in response.meta.keys():
            max_page = response.meta['max_page']
            if max_page:
                next_page = response.xpath("//a[i[@class='material-icons' and text()='chevron_right']]/@href").get()
                next_page_num = int(next_page.split('page_no=')[1].split('&')[0])
                if max_page >= next_page_num:
                    yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse_search,
                                         meta={'max_page': max_page})

    # 处理pdf链接数据
    def capture_redirect(self, response):
        fileVo = FileVo()
        fileVo.src = response.urljoin(response.headers['Location'].decode('utf-8'))
        pdfItem = response.meta['pdfItem']
        pdfItem['pdf'] = fileVo
        yield pdfItem


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process command line arguments')
    parser.add_argument('--case_id', type=str, help='Case ID parameter')
    args = parser.parse_args()
    case_id = args.case_id
    par = {
        "caseId": case_id,
        "taskId": '111',
        "stepId": '111',
        "keywords": "knowledge",
        "max_page": 4
    }
    execute(['scrapy', 'crawl', 'mdpi', '-a', "taskInfo=" + json.dumps(par)])